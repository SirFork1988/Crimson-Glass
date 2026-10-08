#!/usr/bin/env python3
"""Portable optional Crimson Glass SDDM/Plymouth installer (Python stdlib only).

Import install_startup(), restore_startup(), or audit_startup(). Non-/ target roots
are filesystem simulations: external commands never run unless a test supplies
an explicit callable runner. No session restart, reboot, bootloader-option edit,
driver change, or restoration of old kernel/initramfs images is performed.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import tempfile
import uuid

SDDM_THEME = '/usr/share/sddm/themes/CrimsonGlass'
PLYMOUTH_THEME = '/usr/share/plymouth/themes/crimson-glass'
SDDM_CONFIG = '/etc/sddm.conf'
PLYMOUTH_CONFIG = '/etc/plymouth/plymouthd.conf'
DRACUT_CONFIG = '/etc/dracut.conf.d/90-crimson-glass.conf'
BACKUP_BASE = '/var/lib/crimson-glass/startup-backups'
BACKENDS = {'limine-mkinitcpio': [], 'mkinitcpio': ['-P'],
            'update-initramfs': ['-u', '-k', 'all'],
            'dracut': ['--regenerate-all', '--force']}
QML_MODULES = ('QtQuick/Controls', 'QtQuick/Layouts', 'Qt5Compat/GraphicalEffects',
               'org/kde/kirigami', 'org/kde/plasma/components',
               'org/kde/plasma/extras', 'org/kde/plasma/private/keyboardindicator',
               'org/kde/breeze/components')
PRESERVED_PATHS = ('/etc/default/grub', '/etc/default/limine', '/etc/default/limine.d',
                   '/etc/kernel/cmdline', '/etc/cmdline.d', '/boot/loader/loader.conf',
                   '/boot/loader/entries', '/boot/grub/grub.cfg')
DOCUMENTATION = {
    'mkinitcpio': 'https://man.archlinux.org/man/mkinitcpio.8.en',
    'update-initramfs': 'https://manpages.debian.org/trixie/initramfs-tools/update-initramfs.8.en.html',
    'dracut': 'https://dracut-ng.github.io/dracut/man/dracut.8.html',
    'sddm': 'https://github.com/sddm/sddm/blob/develop/data/man/sddm.conf.rst.in',
}


class StartupError(RuntimeError):
    pass


class Target:
    def __init__(self, root='/'):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise StartupError(f'Target root does not exist: {self.root}')
        self.live = self.root == Path('/')

    def path(self, logical):
        logical = PurePosixPath(logical)
        if not logical.is_absolute() or '..' in logical.parts:
            raise StartupError(f'Invalid system path: {logical}')
        path = self.root.joinpath(*logical.parts[1:])
        # A symlink at the final entry can safely be backed up/replaced. Its parent
        # must not redirect a fake target's writes onto the running host.
        if not path.parent.resolve().is_relative_to(self.root):
            raise StartupError(f'Target path escapes root through a parent symlink: {path}')
        return path

    def command(self, name):
        if self.live:
            return shutil.which(name, path='/usr/sbin:/usr/bin:/sbin:/bin')
        for directory in ('usr/sbin', 'usr/bin', 'sbin', 'bin'):
            p = self.root / directory / name
            if p.is_file() and os.access(p, os.X_OK) and p.resolve().is_relative_to(self.root):
                return str(p)
        return None


def _exists(path):
    return path.exists() or path.is_symlink()


def _fingerprint(path):
    if not _exists(path):
        return None
    h = hashlib.sha256()
    paths = [path]
    if path.is_dir() and not path.is_symlink():
        paths += sorted(path.rglob('*'), key=lambda p: str(p.relative_to(path)))
    for p in paths:
        name = '.' if p == path else str(p.relative_to(path))
        h.update(name.encode() + b'\0')
        if p.is_symlink():
            h.update(b'L' + os.readlink(p).encode())
        elif p.is_file():
            h.update(b'F')
            with p.open('rb') as f:
                for block in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(block)
        elif p.is_dir():
            h.update(b'D')
        else:
            raise StartupError(f'Unsupported special file: {p}')
    return h.hexdigest()


def _copy(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_symlink():
        dst.symlink_to(os.readlink(src))
    elif src.is_dir():
        shutil.copytree(src, dst, symlinks=True)
    else:
        shutil.copy2(src, dst)


def _remove(path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _write(path, text, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement does not follow a final symlink.
    fd, tmp = tempfile.mkstemp(prefix='.crimson-glass-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _ini_value(text, section, key):
    active = False
    value = None
    for line in text.splitlines():
        m = re.match(r'^\s*\[([^]]+)\]\s*(?:[#;].*)?$', line)
        if m:
            active = m.group(1) == section
        elif active:
            m = re.match(r'^\s*' + re.escape(key) + r'\s*=\s*(.*?)\s*$', line)
            if m:
                value = m.group(1)
    return value


def _set_ini(text, section, updates):
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if re.match(r'^\s*\[' + re.escape(section) + r'\]\s*$', line.strip())]
    if len(matches) > 1:
        raise StartupError(f'Config has duplicate [{section}] sections; edit it manually first.')
    if not matches:
        return text.rstrip('\n') + ('\n\n' if text.strip() else '') + f'[{section}]\n' + ''.join(f'{k}={v}\n' for k, v in updates.items())
    start = matches[0] + 1
    end = next((i for i in range(start, len(lines)) if re.match(r'^\s*\[', lines[i])), len(lines))
    remaining = dict(updates)
    result = []
    for line in lines[start:end]:
        m = re.match(r'^\s*([^#;=]+?)\s*=', line)
        if m and m.group(1).strip() in updates:
            key = m.group(1).strip()
            if key in remaining:
                result.append(f'{key}={remaining.pop(key)}\n')
        else:
            result.append(line if line.endswith('\n') else line + '\n')
    result += [f'{key}={value}\n' for key, value in remaining.items()]
    return ''.join(lines[:start] + result + lines[end:])


def _read(path):
    return path.read_text() if path.is_file() else ''


def _hooks(text):
    matches = list(re.finditer(r'^\s*HOOKS\s*=\s*\((.*?)\)', text, re.M | re.S))
    if not matches:
        return None
    body = re.sub(r'#[^\n]*', '', matches[-1].group(1))
    if '$' in body or '`' in body:
        return None
    try:
        return shlex.split(body)
    except ValueError:
        return None


def _add_plymouth_hook(text):
    hooks = _hooks(text)
    if not hooks or not any(h in hooks for h in ('systemd', 'udev')):
        raise StartupError('A simple HOOKS array containing systemd or udev is required. Configure the Plymouth hook manually.')
    if 'plymouth' in hooks:
        return text
    hooks.insert(max(i for i, h in enumerate(hooks) if h in ('systemd', 'udev')) + 1, 'plymouth')
    matches = list(re.finditer(r'^\s*HOOKS\s*=\s*\((.*?)\)', text, re.M | re.S))
    match = matches[-1]
    return text[:match.start()] + 'HOOKS=(' + ' '.join(hooks) + ')' + text[match.end():]


def _asset_check(assets, sddm, plymouth):
    assets = Path(assets).resolve()
    sources = {}
    for enabled, sub, destination in ((sddm, 'sddm/CrimsonGlass', SDDM_THEME),
                                       (plymouth, 'plymouth/crimson-glass', PLYMOUTH_THEME)):
        if not enabled:
            continue
        src = assets / sub
        if not src.is_dir() or src.is_symlink() or any(p.is_symlink() for p in src.rglob('*')):
            raise StartupError(f'Missing or non-self-contained theme assets: {src}')
        sources[destination] = src
    if sddm and not (sources[SDDM_THEME] / 'Main.qml').is_file():
        raise StartupError('SDDM theme is missing Main.qml.')
    if plymouth:
        config = _read(sources[PLYMOUTH_THEME] / 'crimson-glass.plymouth')
        if _ini_value(config, 'Plymouth Theme', 'ModuleName') != 'two-step' or _ini_value(config, 'two-step', 'ImageDir') != PLYMOUTH_THEME:
            raise StartupError('Plymouth theme must select two-step and the final /usr/share theme directory.')
        for name in ('background.png', 'watermark.png', 'entry.png', 'bullet.png', 'lock.png', 'animation-0001.png', 'throbber-0001.png'):
            if not (sources[PLYMOUTH_THEME] / name).is_file():
                raise StartupError(f'Plymouth theme asset missing: {name}')
    return sources


def _select_backend(target, requested='auto'):
    available = {name: target.command(name) for name in BACKENDS}
    available = {name: path for name, path in available.items() if path}
    if requested != 'auto':
        if requested not in available:
            raise StartupError(f'Requested initramfs command is unavailable: {requested}')
        return requested, available[requested]
    if 'limine-mkinitcpio' in available and target.path('/etc/default/limine').exists():
        return 'limine-mkinitcpio', available['limine-mkinitcpio']
    release = _read(target.path('/etc/os-release')).lower()
    for pattern, choice in ((r'debian|ubuntu', 'update-initramfs'), (r'fedora|rhel|centos', 'dracut'),
                            (r'arch|cachyos|manjaro', 'mkinitcpio')):
        if re.search(pattern, release) and choice in available:
            return choice, available[choice]
    normal = {name: path for name, path in available.items() if name != 'limine-mkinitcpio'}
    if len(normal) == 1:
        return next(iter(normal.items()))
    if not normal and len(available) == 1:
        return next(iter(available.items()))
    raise StartupError('No unambiguous initramfs backend. Install the distribution tool or choose --backend explicitly.')


def _qml_roots(target):
    roots = [target.path(p) for p in ('/usr/lib/qt6/qml', '/usr/lib64/qt6/qml', '/usr/share/qt6/qml')]
    roots += list(target.path('/usr/lib').glob('*/qt6/qml'))
    return [p for p in roots if p.is_dir()]


def _qt6_greeter(target):
    for directory in ('/usr/bin', '/usr/lib/sddm', '/usr/libexec', '/usr/libexec/sddm'):
        for name in ('sddm-greeter-qt6', 'sddm-greeter'):
            path = target.path(directory) / name
            if path.is_file() and os.access(path, os.X_OK):
                if name.endswith('-qt6') or b'libQt6' in path.read_bytes():
                    return str(path)
    return None


def audit_startup(assets, target_root='/', sddm=False, plymouth=False, backend='auto', enable_mkinitcpio_hook=False):
    target = Target(target_root)
    sources = _asset_check(assets, sddm, plymouth)
    report = {'target_root': str(target.root), 'simulation': not target.live, 'sddm': sddm, 'plymouth': plymouth,
              'errors': [], 'warnings': [], 'changes': list(sources), 'backend': None, 'rebuild_command': None,
              'reboot_performed': False, 'sddm_restarted': False, 'documentation': DOCUMENTATION}
    if not sddm and not plymouth:
        report['errors'].append('Choose at least one optional component: SDDM and/or Plymouth.')
    if sddm:
        if not target.command('sddm'):
            report['errors'].append('SDDM is not installed; another login manager will not use this theme.')
        if not _qt6_greeter(target):
            report['errors'].append('A Qt6 SDDM greeter is required; the Qt5 greeter cannot load this Plasma 6 theme.')
        roots = _qml_roots(target)
        missing = [module for module in QML_MODULES if not any((root / module / 'qmldir').is_file() for root in roots)]
        if missing:
            report['errors'].append('Missing Qt6/Plasma 6 QML modules: ' + ', '.join(missing))
        report['changes'].append(SDDM_CONFIG)
    if plymouth:
        if not target.command('plymouth') or not target.command('plymouthd'):
            report['errors'].append('Plymouth daemon/client packages are required.')
        plugins = [target.path(p) for p in ('/usr/lib/plymouth/two-step.so', '/usr/lib64/plymouth/two-step.so')]
        plugins += list(target.path('/usr/lib').glob('*/plymouth/two-step.so'))
        if not any(p.is_file() for p in plugins):
            report['errors'].append('Plymouth native two-step plugin is missing (often in a Plymouth themes/renderers package).')
        try:
            name, command = _select_backend(target, backend)
            report['backend'] = name
            report['rebuild_command'] = [command, *BACKENDS[name]]
            inspection_tool = {'limine-mkinitcpio': 'lsinitcpio', 'mkinitcpio': 'lsinitcpio',
                               'update-initramfs': 'lsinitramfs', 'dracut': 'lsinitrd'}[name]
            if not target.command(inspection_tool):
                report['errors'].append(f'The distribution image inspection tool is missing: {inspection_tool}.')
            if name in ('mkinitcpio', 'limine-mkinitcpio'):
                config = _read(target.path('/etc/mkinitcpio.conf'))
                hooks = _hooks(config)
                drops = target.path('/etc/mkinitcpio.conf.d')
                # A later drop-in may assign HOOKS. Presets using -c ignore drops,
                # so the main config must also include Plymouth for portability.
                assignments = [(str(p), _hooks(_read(p))) for p in sorted(drops.glob('*.conf'))] if drops.is_dir() else []
                report['mkinitcpio_main_hooks'] = hooks
                report['mkinitcpio_dropin_hook_assignments'] = [(p, h) for p, h in assignments if h is not None]
                if not hooks or 'plymouth' not in hooks:
                    if enable_mkinitcpio_hook:
                        _add_plymouth_hook(config)
                        report['changes'].append('/etc/mkinitcpio.conf')
                    else:
                        report['errors'].append('Main mkinitcpio HOOKS lacks plymouth. Use --enable-mkinitcpio-hook for a guarded hook-only edit, or configure it manually.')
                if assignments and any(h is not None and 'plymouth' not in h for _, h in assignments):
                    report['errors'].append('A mkinitcpio drop-in overrides HOOKS without plymouth; update that drop-in manually first.')
                if not target.path('/usr/lib/initcpio/install/plymouth').is_file():
                    report['errors'].append('The mkinitcpio Plymouth install hook is missing.')
                if name == 'mkinitcpio' and not list(target.path('/etc/mkinitcpio.d').glob('*.preset')):
                    report['errors'].append('No mkinitcpio presets found; automatic rebuild cannot choose image paths.')
            elif name == 'update-initramfs':
                if not target.path('/usr/share/initramfs-tools/hooks/plymouth').is_file():
                    report['errors'].append('The distribution Plymouth initramfs-tools hook is missing.')
            elif name == 'dracut':
                modules = [target.path(p) for p in ('/usr/lib/dracut/modules.d/50plymouth', '/usr/lib64/dracut/modules.d/50plymouth')]
                if not any(p.is_dir() for p in modules):
                    report['errors'].append('The distribution dracut Plymouth module is missing.')
                report['changes'].append(DRACUT_CONFIG)
        except StartupError as error:
            report['errors'].append(str(error))
        report['changes'].append(PLYMOUTH_CONFIG)
        cmdline = _read(target.path('/proc/cmdline')).strip()
        report['running_kernel_has_splash'] = 'splash' in shlex.split(cmdline) if cmdline else None
        if not report['running_kernel_has_splash']:
            report['warnings'].append('The running kernel command line does not show splash. Add splash manually to the active bootloader/kernel command line and regenerate its config using your distribution instructions. This installer preserves those options.')
        report['warnings'].append('Initramfs regeneration uses the installed distribution tools and current kernels. No saved boot images are restored, including after kernel upgrades.')
    report['warnings'].append('Noto Sans is preferred by the bundled theme; install it if exact typography is required.')
    report['changes'] = list(dict.fromkeys(report['changes']))
    return report


@contextlib.contextmanager
def _lock(target):
    path = target.path('/run/lock/crimson-glass-startup.lock')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise StartupError('Startup lock is an unsafe symlink.')
    with path.open('a') as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise StartupError('Another Crimson Glass startup operation is running.') from error
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def _new_backup(target, changes, report):
    base = target.path(BACKUP_BASE)
    if base.is_symlink():
        raise StartupError('Startup backup directory is an unsafe symlink.')
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(base, 0o700)
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    backup = base / stamp
    backup.mkdir(mode=0o700)
    manifest = {'format': 1, 'created': stamp, 'components': {'sddm': report['sddm'], 'plymouth': report['plymouth']},
                'backend': report['backend'], 'entries': [], 'state': 'backed-up', 'simulation': not target.live}
    for logical in changes:
        path = target.path(logical)
        before = _fingerprint(path)
        item = {'path': logical, 'before': before, 'after': None, 'saved': before is not None}
        if before is not None:
            _copy(path, backup / 'files' / logical.lstrip('/'))
            if _fingerprint(backup / 'files' / logical.lstrip('/')) != before:
                raise StartupError(f'Backup copy verification failed: {logical}')
        manifest['entries'].append(item)
    _write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n', 0o600)
    # Only a completed backup is advertised; failures cannot point latest at a partial copy.
    _write(base / 'latest', stamp + '\n', 0o600)
    return backup, manifest


def _run(target, command, backup, runner=None):
    with (backup / 'commands.jsonl').open('a') as f:
        f.write(json.dumps({'command': command, 'simulated': not target.live and runner is None}) + '\n')
    if not target.live and runner is None:
        return None
    if runner is not None:
        return runner(list(command))
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=1800,
                            env={**os.environ, 'PATH': '/usr/sbin:/usr/bin:/sbin:/bin'})
    with (backup / 'initramfs.log').open('a') as f:
        f.write('+ ' + shlex.join(command) + '\n' + result.stdout + '\n')
    if result.returncode:
        raise StartupError(f'Initramfs command failed ({result.returncode}); see {backup / "initramfs.log"}')
    return result.stdout


def _initramfs_images(target, backend):
    images = []
    if backend == 'mkinitcpio':
        for preset in target.path('/etc/mkinitcpio.d').glob('*.preset'):
            for match in re.finditer(r'^\s*\w+_image\s*=\s*[\"\']([^\"\']+)[\"\']', _read(preset), re.M):
                logical = match.group(1)
                if logical.startswith('/') and not any(s in logical for s in ('$', '`')):
                    images.append(target.path(logical))
    if images:
        return sorted(set(images))
    boot = target.path('/boot')
    modules = target.path('/usr/lib/modules')
    versions = {p.name for p in modules.iterdir() if p.is_dir()} if modules.is_dir() else set()
    if boot.is_dir():
        for path in boot.rglob('*'):
            if any('snapshot' in component.lower() for component in path.relative_to(boot).parts):
                continue
            name = path.name
            # Rescue images are intentionally not regenerated by dracut's all-
            # kernels command. Orphaned images also must not block verification.
            if 'rescue' in name.lower():
                continue
            if backend == 'dracut' and versions and name.startswith('initramfs-') and name.endswith('.img'):
                if name[len('initramfs-'):-len('.img')] not in versions:
                    continue
            if backend == 'update-initramfs' and versions and name.startswith('initrd.img-'):
                if name[len('initrd.img-'):] not in versions:
                    continue
            if path.is_file() and (name in ('initramfs', 'initramfs-fallback', 'initrd') or
                                   name.startswith('initrd.img-') or
                                   (name.startswith(('initramfs-', 'initrd-')) and name.endswith('.img'))):
                images.append(path)
    if backend == 'limine-mkinitcpio':
        bases = {p.read_text().strip() for p in target.path('/usr/lib/modules').glob('*/pkgbase')}
        if bases:
            images = [path for path in images if path.parent.name in bases]
            missing = sorted(bases - {path.parent.name for path in images})
            if missing:
                raise StartupError('Cannot verify Limine initramfs for installed kernel base(s): ' + ', '.join(missing) + '. UKI-only/custom paths need manual integration.')
    return sorted(set(images))


def _verify_initramfs(target, backend, backup, runner=None):
    tool = {'limine-mkinitcpio': 'lsinitcpio', 'mkinitcpio': 'lsinitcpio',
            'update-initramfs': 'lsinitramfs', 'dracut': 'lsinitrd'}[backend]
    executable = target.command(tool)
    if not target.live and runner is None:
        return {'status': 'simulated; initramfs commands were not executed', 'images': []}
    if not executable:
        raise StartupError(f'Cannot verify rebuilt image contents: {tool} is missing.')
    images = _initramfs_images(target, backend)
    if not images:
        raise StartupError('No inspectable initramfs image paths found; custom/UKI-only layouts require manual integration.')
    verified = []
    for image in images:
        if not image.is_file():
            raise StartupError(f'Configured initramfs image is missing: {image}')
        command = [executable, '--list', str(image)] if tool == 'lsinitcpio' else [executable, str(image)]
        listing = _run(target, command, backup, runner)
        if not isinstance(listing, str):
            raise StartupError(f'Image listing is unavailable for {image}')
        for token in ('usr/share/plymouth/themes/crimson-glass/crimson-glass.plymouth',
                      'usr/share/plymouth/themes/crimson-glass/background.png',
                      'usr/share/plymouth/themes/crimson-glass/watermark.png', 'two-step.so'):
            if token not in listing:
                raise StartupError(f'Rebuilt initramfs is missing {token}: {image}')
        verified.append({'path': str(image), 'fingerprint': _fingerprint(image)})
    return {'status': 'theme assets and native plugin found in every discovered current image', 'images': verified}


def _preserved(target):
    result = {logical: _fingerprint(target.path(logical)) for logical in PRESERVED_PATHS}
    # Preserve kernel boot arguments in generated Limine configs; helper-generated
    # initramfs paths/checksums must stay synchronized with the newly built images.
    for logical in ('/boot/limine.conf', '/boot/EFI/limine/limine.conf'):
        path = target.path(logical)
        if path.is_file():
            result[logical + ':cmdline'] = sorted(line.strip() for line in _read(path).splitlines()
                                                  if re.match(r'\s*(?:cmdline|kernel_cmdline)\s*[:=]', line, re.I))
    return result


def _verify_preserved(target, before):
    after = _preserved(target)
    for logical, value in before.items():
        if after.get(logical) != value:
            raise StartupError(f'Initramfs tooling changed an authored boot setting unexpectedly: {logical}')


def _restore_files(target, backup, manifest):
    for entry in reversed(manifest['entries']):
        destination = target.path(entry['path'])
        source = backup / 'files' / entry['path'].lstrip('/')
        _remove(destination)
        if entry['saved']:
            if _fingerprint(source) != entry['before']:
                raise StartupError(f'Backup integrity mismatch: {entry["path"]}')
            _copy(source, destination)


def install_startup(assets, target_root='/', sddm=False, plymouth=False, backend='auto',
                    enable_mkinitcpio_hook=False, runner=None, dry_run=False):
    target = Target(target_root)
    report = audit_startup(assets, target_root, sddm, plymouth, backend, enable_mkinitcpio_hook)
    if report['errors']:
        raise StartupError('; '.join(report['errors']))
    if dry_run:
        return report
    if target.live and os.geteuid() != 0:
        raise StartupError('System installation requires administrator privileges; rerun this command with sudo.')
    sources = _asset_check(assets, sddm, plymouth)
    with _lock(target):
        preserved = _preserved(target)
        backup, manifest = _new_backup(target, report['changes'], report)
        report['backup'] = str(backup)
        manifest['preserved_boot_settings'] = preserved
        _write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n', 0o600)
        try:
            for logical, source in sources.items():
                destination = target.path(logical)
                _remove(destination)
                _copy(source, destination)
                for path in [destination, *destination.rglob('*')]:
                    os.chmod(path, 0o755 if path.is_dir() else 0o644)
            if sddm:
                path = target.path(SDDM_CONFIG)
                _write(path, _set_ini(_read(path), 'Theme', {'Current': 'CrimsonGlass', 'ThemeDir': '/usr/share/sddm/themes'}))
            if plymouth:
                path = target.path(PLYMOUTH_CONFIG)
                _write(path, _set_ini(_read(path), 'Daemon', {'Theme': 'crimson-glass'}))
                if '/etc/mkinitcpio.conf' in report['changes']:
                    path = target.path('/etc/mkinitcpio.conf')
                    _write(path, _add_plymouth_hook(_read(path)))
                if report['backend'] == 'dracut':
                    path = target.path(DRACUT_CONFIG)
                    text = _read(path)
                    directive = 'add_dracutmodules+=" plymouth "'
                    if directive not in text.splitlines():
                        _write(path, text.rstrip('\n') + ('\n' if text else '') + '# Crimson Glass: use the installed Plymouth module.\n' + directive + '\n')
                _run(target, report['rebuild_command'], backup, runner)
                report['initramfs_verification'] = _verify_initramfs(target, report['backend'], backup, runner)
            _verify_preserved(target, preserved)
            for entry in manifest['entries']:
                entry['after'] = _fingerprint(target.path(entry['path']))
            manifest['state'] = 'installed'
            _write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n', 0o600)
            report['commands_executed'] = target.live or runner is not None
            report['installed_assets_verified'] = all(_fingerprint(target.path(p)) == _fingerprint(src) for p, src in sources.items())
            if not report['installed_assets_verified']:
                raise StartupError('Installed theme asset integrity mismatch.')
            _write(backup / 'report.json', json.dumps(report, indent=2) + '\n', 0o600)
            return report
        except Exception as error:
            _restore_files(target, backup, manifest)
            manifest['state'] = 'rolled-back'
            manifest['error'] = str(error)
            if plymouth:
                try:
                    _run(target, report['rebuild_command'], backup, runner)
                    manifest['rollback_initramfs_rebuilt'] = True
                except Exception as rebuild_error:
                    manifest['rollback_initramfs_rebuilt'] = False
                    manifest['rollback_rebuild_error'] = str(rebuild_error)
            _write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n', 0o600)
            raise StartupError(f'Installation failed; original theme/config files restored. Backup: {backup}. '
                               f'Rollback initramfs rebuilt: {manifest.get("rollback_initramfs_rebuilt", "not needed")}. {error}') from error


def restore_startup(backup=None, target_root='/', backend='auto', runner=None, force=False, dry_run=False):
    target = Target(target_root)
    base = target.path(BACKUP_BASE)
    if backup is None:
        name = _read(base / 'latest').strip()
        if not name or Path(name).name != name:
            raise StartupError('No valid latest startup backup.')
        backup = base / name
    else:
        backup = Path(backup).resolve()
    if not backup.is_dir() or backup.is_symlink():
        raise StartupError('Backup directory is missing or unsafe.')
    manifest = json.loads((backup / 'manifest.json').read_text())
    if manifest.get('format') != 1 or manifest.get('state') not in ('installed', 'restored', 'rolled-back'):
        raise StartupError('Backup is incomplete or unsupported.')
    if bool(manifest.get('simulation')) != (not target.live):
        raise StartupError('A simulated-root backup cannot be restored onto the running system, or vice versa.')
    allowed = {SDDM_THEME, PLYMOUTH_THEME, SDDM_CONFIG, PLYMOUTH_CONFIG, DRACUT_CONFIG, '/etc/mkinitcpio.conf'}
    for entry in manifest['entries']:
        if entry['path'] not in allowed:
            raise StartupError('Backup contains an unexpected system destination.')
        if entry['saved'] and _fingerprint(backup / 'files' / entry['path'].lstrip('/')) != entry['before']:
            raise StartupError(f'Backup integrity mismatch: {entry["path"]}')
        current = _fingerprint(target.path(entry['path']))
        if not force and current not in (entry.get('after'), entry['before']):
            raise StartupError(f'File changed since installation: {entry["path"]}. Inspect it or use --force-restore explicitly.')
    command = None
    if manifest['components']['plymouth']:
        name, executable = _select_backend(target, backend)
        command = [executable, *BACKENDS[name]]
    report = {'backup': str(backup), 'restored_paths': [entry['path'] for entry in manifest['entries']],
              'rebuild_command': command, 'simulation': not target.live, 'reboot_performed': False, 'sddm_restarted': False,
              'boot_images_restored': False}
    if dry_run:
        return report
    if target.live and os.geteuid() != 0:
        raise StartupError('System restore requires administrator privileges; rerun with sudo.')
    with _lock(target):
        preserved = _preserved(target)
        _restore_files(target, backup, manifest)
        if command:
            _run(target, command, backup, runner)
        _verify_preserved(target, preserved)
        manifest['state'] = 'restored'
        manifest['restored_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
        _write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n', 0o600)
        _write(backup / 'restore-report.json', json.dumps(report, indent=2) + '\n', 0o600)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('audit', 'install', 'restore'))
    parser.add_argument('--assets', type=Path, help='Root containing sddm/CrimsonGlass and plymouth/crimson-glass.')
    parser.add_argument('--target-root', default='/', help='Non-/ roots simulate system writes and never execute host tools.')
    parser.add_argument('--sddm', '--login', dest='sddm', action='store_true', help='Opt in to the matching Plasma 6 SDDM login theme.')
    parser.add_argument('--plymouth', '--boot', dest='plymouth', action='store_true', help='Opt in to the matching native Plymouth boot theme.')
    parser.add_argument('--backend', choices=('auto', *BACKENDS), default='auto')
    parser.add_argument('--enable-mkinitcpio-hook', '--configure-initramfs', dest='enable_mkinitcpio_hook', action='store_true', help='Permit adding plymouth after systemd/udev in a simple main HOOKS array.')
    parser.add_argument('--backup', type=Path, help='Restore this startup backup; omitted means latest.')
    parser.add_argument('--force-restore', action='store_true', help='Permit restoring files edited after installation.')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        if args.action == 'restore':
            report = restore_startup(args.backup, args.target_root, args.backend, force=args.force_restore, dry_run=args.dry_run)
        else:
            if args.assets is None:
                parser.error('--assets is required for audit/install.')
            call = audit_startup if args.action == 'audit' else install_startup
            kwargs = {'sddm': args.sddm, 'plymouth': args.plymouth, 'backend': args.backend,
                      'enable_mkinitcpio_hook': args.enable_mkinitcpio_hook}
            if args.action == 'install':
                kwargs['dry_run'] = args.dry_run
            report = call(args.assets, args.target_root, **kwargs)
        print(json.dumps(report, indent=2))
        return 1 if report.get('errors') else 0
    except (StartupError, OSError, ValueError) as error:
        print(f'Crimson Glass startup: {error}', file=__import__('sys').stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
