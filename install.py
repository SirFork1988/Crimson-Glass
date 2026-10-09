#!/usr/bin/env python3
"""Crimson Glass 1.1.0: backed-up, portable KDE Plasma 6 theme installer."""
# SPDX-License-Identifier: MIT
from __future__ import annotations
import argparse, datetime, hashlib, json, os, re, shlex, shutil, subprocess, sys
import tarfile, tempfile, time, uuid
from pathlib import Path, PurePosixPath
import dependencies, runtime_install

if sys.version_info < (3,10):
    raise SystemExit('Crimson Glass requires Python 3.10 or newer.')

BASE=Path(__file__).resolve().parent
VERSION='1.1.0'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def verify():
    manifest=json.loads((BASE/'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        p=BASE/name
        if '..' in PurePosixPath(name).parts or PurePosixPath(name).is_absolute() or not p.is_file():
            raise RuntimeError('Missing or unsafe release file: '+name)
        if digest(p)!=expected: raise RuntimeError('Release integrity check failed: '+name)
    print('Verified bundled files (SHA-256).',flush=True)
    return manifest

def extract_assets(destination):
    """Extract only directories, regular files and confined relative symlinks."""
    with tarfile.open(BASE/'assets.tar.xz','r:xz') as tf:
        entries=tf.getmembers(); seen=set(); links=[]
        for entry in entries:
            p=PurePosixPath(entry.name)
            if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] not in ('data','config','system'):
                raise RuntimeError('Unsafe archive member: '+entry.name)
            if entry.name in seen: raise RuntimeError('Duplicate archive member: '+entry.name)
            seen.add(entry.name)
            if not (entry.isdir() or entry.isfile() or entry.issym()):
                raise RuntimeError('Unsupported archive entry: '+entry.name)
            if entry.issym():
                if PurePosixPath(entry.linkname).is_absolute(): raise RuntimeError('Absolute asset link: '+entry.name)
                target=destination.joinpath(*p.parent.parts,entry.linkname)
                if not target.resolve().is_relative_to(destination): raise RuntimeError('Escaping asset link: '+entry.name)
                links.append(entry)
        # Symlinks are created last, so an archive link cannot redirect a file write.
        for entry in entries:
            if entry.issym(): continue
            path=destination/entry.name
            path.parent.mkdir(parents=True,exist_ok=True)
            if entry.isdir(): path.mkdir(exist_ok=True)
            else:
                with tf.extractfile(entry) as src, path.open('wb') as dst: shutil.copyfileobj(src,dst)
                path.chmod(entry.mode & 0o777)
        for entry in links:
            path=destination/entry.name
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() or path.is_symlink(): raise RuntimeError('Archive link overlaps a file: '+entry.name)
            path.symlink_to(entry.linkname)
        for entry in links:
            path=destination/entry.name
            if not path.resolve().is_relative_to(destination) or not path.exists():
                raise RuntimeError('Broken or escaping asset link: '+entry.name)

def run(args, check=True, capture=False):
    return subprocess.run([str(x) for x in args],check=check,text=True,
        stdout=subprocess.PIPE if capture else None,stderr=subprocess.PIPE if capture else None)

def qdbus():
    for name in ['qdbus6','qdbus-qt6','qdbus']:
        if shutil.which(name): return shutil.which(name)
    for name in ['/usr/lib/qt6/bin/qdbus','/usr/lib64/qt6/bin/qdbus','/usr/lib/qt6/libexec/qdbus']:
        if Path(name).is_file(): return name
    raise RuntimeError('Qt6 qdbus is missing. Install the Qt6 tools package.')

def plasma_check(live):
    if not shutil.which('plasmashell'): raise RuntimeError('Install KDE Plasma 6 first; this package themes an existing KDE desktop.')
    r=run(['plasmashell','--version'],capture=True)
    m=re.search(r'plasmashell\s+(\d+)\.(\d+)',r.stdout+r.stderr)
    if not m or int(m[1])!=6: raise RuntimeError('KDE Plasma 6 is required. Plasma 5 is unsupported.')
    if live:
        result=run([qdbus(),'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript','print("Crimson Glass preflight");'],capture=True)
        if 'Crimson Glass preflight' not in result.stdout: raise RuntimeError('Run the installer inside your normal KDE Plasma session.')

def ini_updates(path, groups):
    """Merge keys without destroying unrelated KConfig groups or preferences."""
    text=path.read_text() if path.exists() else ''
    lines=text.splitlines(keepends=True)
    for group, values in groups.items():
        header='['+group+']'
        starts=[i for i,line in enumerate(lines) if line.strip()==header]
        if len(starts)>1: raise RuntimeError('Duplicate config group '+header+' in '+str(path))
        if not starts:
            if lines and not lines[-1].endswith('\n'): lines[-1]+='\n'
            lines+=['\n',header+'\n']+[k+'='+str(v)+'\n' for k,v in values.items()]
            continue
        start=starts[0]+1
        end=next((i for i in range(start,len(lines)) if lines[i].startswith('[')),len(lines))
        left=dict(values); updated=[]
        for line in lines[start:end]:
            key=line.split('=',1)[0].strip() if '=' in line and not line.lstrip().startswith(('#',';')) else None
            if key in values:
                if key in left: updated.append(key+'='+str(left.pop(key))+'\n')
            else: updated.append(line if line.endswith('\n') else line+'\n')
        updated.extend(k+'='+str(v)+'\n' for k,v in left.items())
        lines[start:end]=updated
    atomic_write(path,''.join(lines))

def atomic_write(path, text):
    path.parent.mkdir(parents=True,exist_ok=True)
    mode=(path.stat().st_mode & 0o777) if path.exists() and not path.is_symlink() else 0o600
    with tempfile.NamedTemporaryFile(mode='w',prefix='.crimson-',dir=path.parent,delete=False) as f:
        f.write(text); tmp=Path(f.name)
    tmp.chmod(mode)
    os.replace(tmp,path)

def exists(path): return path.exists() or path.is_symlink()
def remove(path):
    if path.is_symlink() or path.is_file(): path.unlink()
    elif path.is_dir(): shutil.rmtree(path)
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if src.is_symlink(): dst.symlink_to(os.readlink(src))
    elif src.is_dir(): shutil.copytree(src,dst,symlinks=True)
    else: shutil.copy2(src,dst)

class Home:
    def __init__(self, args):
        self.home=Path(args.home).expanduser().resolve() if args.home else Path.home()
        isolated=bool(args.home)
        self.config=Path(os.environ.get('XDG_CONFIG_HOME',str(self.home/'.config'))) if not isolated else self.home/'.config'
        self.data=Path(os.environ.get('XDG_DATA_HOME',str(self.home/'.local/share'))) if not isolated else self.home/'.local/share'
        self.state=Path(os.environ.get('XDG_STATE_HOME',str(self.home/'.local/state'))) if not isolated else self.home/'.local/state'
        for root in (self.config,self.data,self.state):
            if not root.is_absolute(): raise RuntimeError('XDG paths must be absolute.')
        self.backups=self.state/'crimson-glass/backups'
    def dest(self,scope,name):
        if scope not in ('config','data','home'): raise RuntimeError('Unexpected backup scope.')
        root={'config':self.config,'data':self.data,'home':self.home}[scope]
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts: raise RuntimeError('Unsafe destination path.')
        result=root.joinpath(*p.parts)
        if not result.parent.resolve().is_relative_to(root.resolve()): raise RuntimeError('Destination escapes through a parent link: '+str(result))
        return result

def destinations(assets, settings):
    items=set(runtime_install.ITEMS)
    # Top-level theme directories are copied as units, preserving every alias.
    for p in (assets/'data').rglob('*'):
        rel=p.relative_to(assets/'data')
        if len(rel.parts)==2 and rel.parts[0] in ('icons','themes','wallpapers','konsole','color-schemes'):
            items.add(('data',str(rel)))
        elif len(rel.parts)==3 and rel.parts[0]=='plasma' and rel.parts[1] in ('desktoptheme','plasmoids','look-and-feel'):
            items.add(('data',str(rel)))
        elif len(rel.parts)==3 and rel.parts[:2]==('aurorae','themes'):
            items.add(('data',str(rel)))
    for p in (assets/'config/Kvantum').iterdir(): items.add(('config','Kvantum/'+p.name))
    items.add(('config','gtk-4.0'))
    items.update(('config',s) for s in settings)
    items.update(('config',s) for s in ['gtk-3.0/settings.ini','gtk-3.0/gtk.css','gtk-3.0/colors.css','xsettingsd/xsettingsd.conf','plasma-org.kde.plasma.desktop-appletsrc','plasma-workspace/env/90-crimson-glass.sh'])
    items.add(('home','.gtkrc-2.0'))
    items.add(('data','dolphin/view_properties/global'))
    # Parent directories are enough; nested entries would create conflicting restores.
    return sorted(i for i in items if not any(i[0]==j[0] and i[1].startswith(j[1]+'/') for j in items if i!=j))

def snapshot(home, items):
    name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    backup=home.backups/name; backup.mkdir(parents=True,mode=0o700)
    entries=[]
    for scope, name in items:
        target=home.dest(scope,name); saved=exists(target)
        if saved: copy(target,backup/'files'/scope/name)
        entries.append({'scope':scope,'name':name,'existed':saved})
    metadata={'format':1,'version':VERSION,'status':'saved','roots':{'home':str(home.home),'config':str(home.config),'data':str(home.data)},'entries':entries}
    atomic_write(backup/'backup.json',json.dumps(metadata,indent=2)+'\n')
    atomic_write(home.backups/'latest',backup.name+'\n')
    print('Backup: '+str(backup),flush=True)
    return backup,metadata

def restore_files(home, backup):
    meta=json.loads((backup/'backup.json').read_text())
    if meta.get('format')!=1 or meta['roots']!={'home':str(home.home),'config':str(home.config),'data':str(home.data)}:
        raise RuntimeError('Backup belongs to another home/XDG layout or has an unsupported format.')
    for entry in meta['entries']:
        target=home.dest(entry['scope'],entry['name'])
        saved=backup/'files'/entry['scope']/entry['name']
        if entry['existed'] and not exists(saved): raise RuntimeError('Incomplete backup: '+str(saved))
    for entry in meta['entries']:
        target=home.dest(entry['scope'],entry['name']); remove(target)
        if entry['existed']: copy(backup/'files'/entry['scope']/entry['name'],target)
    meta['status']='restored'; atomic_write(backup/'backup.json',json.dumps(meta,indent=2)+'\n')

def stop_shell():
    # Stop only the user's shell; KWin/session/applications continue running.
    if shutil.which('systemctl'):
        r=run(['systemctl','--user','is-active','plasma-plasmashell.service'],check=False,capture=True)
        if r.returncode==0:
            run(['systemctl','--user','stop','plasma-plasmashell.service']); return 'systemd'
    if shutil.which('kquitapp6'):
        run(['kquitapp6','plasmashell']); return 'manual'
    raise RuntimeError('Log out of KDE and restore from a text console with --offline so Plasma does not overwrite the saved panel config.')

def start_shell(mode):
    if mode=='systemd': run(['systemctl','--user','start','plasma-plasmashell.service'])
    elif mode=='manual': subprocess.Popen(['plasmashell'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)

def gtk_settings(home):
    values={'gtk-theme-name':'CrimsonGlass-Dark-red','gtk-icon-theme-name':'CrimsonGlass-Icons',
     'gtk-cursor-theme-name':'Qogir-Dark','gtk-cursor-theme-size':'24','gtk-font-name':'Noto Sans 10',
     'gtk-application-prefer-dark-theme':'true','gtk-decoration-layout':'close,minimize,maximize:',
     'gtk-enable-animations':'true'}
    for version in ('3.0','4.0'): ini_updates(home.config/('gtk-'+version)/'settings.ini',{'Settings':values})
    # Export traditional GTK3 menus. Keep any pre-existing module names.
    path=home.config/'gtk-3.0/settings.ini'
    match=re.search(r'^gtk-modules=(.*)$',path.read_text(),re.M)
    modules=(match[1].split(':') if match else [])+['colorreload-gtk-module','appmenu-gtk-module']
    ini_updates(path,{'Settings':{'gtk-modules':':'.join(dict.fromkeys(m for m in modules if m)),'gtk-shell-shows-menubar':'1'}})
    path=home.home/'.gtkrc-2.0'
    old=path.read_text() if path.exists() else ''
    old=re.sub(r'\n?# BEGIN CRIMSON GLASS\n.*?# END CRIMSON GLASS\n?', '\n',old,flags=re.S)
    # Explicit values at the end override earlier theme preferences and restore cleanly.
    block='\n# BEGIN CRIMSON GLASS\n'+''.join(f'{k}="{v}"\n' for k,v in values.items() if k not in ('gtk-application-prefer-dark-theme','gtk-enable-animations'))+'# END CRIMSON GLASS\n'
    atomic_write(path,old.rstrip()+block)
    atomic_write(home.config/'gtk-3.0/gtk.css',"@import 'colors.css';\n")
    path=home.config/'xsettingsd/xsettingsd.conf'
    old=path.read_text() if path.exists() else ''
    updates={'Net/ThemeName':'"CrimsonGlass-Dark-red"','Net/IconThemeName':'"CrimsonGlass-Icons"',
      'Gtk/CursorThemeName':'"Qogir-Dark"','Gtk/CursorThemeSize':'24','Gtk/FontName':'"Noto Sans 10"',
      'Gtk/DecorationLayout':'"close,minimize,maximize:"','Gtk/EnableAnimations':'1'}
    lines=[l for l in old.splitlines() if not any(l.split() and l.split()[0]==k for k in updates)]
    lines += [k+' '+v for k,v in updates.items()]
    atomic_write(path,'\n'.join(lines)+'\n')
    # Plasma sources this on next login. Avoid QT_STYLE_OVERRIDE, which breaks QML applications.
    atomic_write(home.config/'plasma-workspace/env/90-crimson-glass.sh',
      '#!/bin/sh\n# Crimson Glass: traditional GTK menu export, preserving other modules.\ncase ":${GTK_MODULES-}:" in\n  *:appmenu-gtk-module:*) ;;\n  *) export GTK_MODULES="${GTK_MODULES:+${GTK_MODULES}:}appmenu-gtk-module" ;;\nesac\n')
    (home.config/'plasma-workspace/env/90-crimson-glass.sh').chmod(0o755)

def apply_assets(home, assets, items, register_launcher=False):
    for scope,name in items:
        source=assets/scope/name
        if not exists(source): continue
        target=home.dest(scope,name)
        if register_launcher and name=='plasma/plasmoids/com.github.SnoutBug.mmckLauncher' and not exists(target):
            if not shutil.which('kpackagetool6'): raise RuntimeError('kpackagetool6 is required to register the bundled launcher.')
            result=run(['kpackagetool6','--type','Plasma/Applet','--install',source],capture=True,check=False)
            if result.returncode and not exists(target):
                # A system-wide copy may already register the ID; our user copy supplies
                # the release version without modifying the distribution-owned package.
                print('KPackage registration: '+(result.stdout+result.stderr).strip())
        if scope=='config' and name=='gtk-4.0':
            # Keep settings and application bookmarks; replace only the theme's CSS/assets.
            if target.is_symlink(): remove(target)
            target.mkdir(parents=True,exist_ok=True)
            for child in source.iterdir(): remove(target/child.name); copy(child,target/child.name)
        else: remove(target); copy(source,target)

def configure_dolphin(home):
    p=home.data/'dolphin/view_properties/global'
    if p.is_symlink(): remove(p)
    p.mkdir(parents=True,exist_ok=True)
    key='user.kde.fm.viewproperties#1'
    try:
        old=os.getxattr(p,key).decode() if key in os.listxattr(p) else ''
        # Preserve the recipient's sort and hidden-file choices; enable the previews shown in the theme.
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'view'; f.write_text(old)
            ini_updates(f,{'Dolphin':{'PreviewsShown':'true','Version':'4'}})
            os.setxattr(p,key,f.read_bytes())
    except (OSError,UnicodeError) as error: print('Dolphin preview preference could not be stored: '+str(error),file=sys.stderr)

def live_apply(home, assets, layout):
    for command in ['kbuildsycoca6']:
        if shutil.which(command): run([command,'--noincremental'])
    # Fresh launcher registration was performed before copying the package. Existing
    # equal-version packages are already registered and must not be upgraded to themselves.
    for command, args in [('plasma-apply-colorscheme',['CrimsonGlass']),('plasma-apply-desktoptheme',['CrimsonGlass'])]:
        if shutil.which(command): run([command,*args])
    if layout:
        # KPackage's short startup cache can temporarily omit a new widget.
        # Readiness probes cannot change the existing desktop/panel layout.
        deadline=time.monotonic()+25
        while True:
            probe=run([qdbus(),'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',
                'print(knownWidgetTypes.indexOf("com.github.SnoutBug.mmckLauncher") >= 0);'],capture=True)
            if probe.stdout.strip()=='true': break
            if time.monotonic()>=deadline: raise RuntimeError('Plasma has not discovered the Andromeda launcher. Log out/back in, then rerun the installer; your saved layout is still available.')
            time.sleep(1)
        uri=(home.data/'wallpapers/CrimsonGlass/CrimsonGlass.png').as_uri()
        script=(BASE/'layout.js').read_text().replace('"__WALLPAPER_URI__"',json.dumps(uri))
        # Resolve this computer's root disk instead of distributing a device identifier.
        try:
            disk=run(['findmnt','-n','-o','UUID','/'],capture=True).stdout.strip()
            if disk and re.fullmatch(r'[A-Za-z0-9._-]+',disk):
                sensors=run([qdbus(),'--literal','org.kde.ksystemstats1','/org/kde/ksystemstats1','org.kde.ksystemstats1.allSensors'],capture=True,check=False)
                if 'disk/'+disk+'/usedPercent' in sensors.stdout:
                    script='var crimsonLayoutOptions='+json.dumps({'rootDiskSensorPrefix':'disk/'+disk})+';\n'+script
        except (OSError,subprocess.CalledProcessError): pass
        result=run([qdbus(),'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',script],capture=True)
        if '"layout":"Crimson Glass"' not in result.stdout:
            raise RuntimeError('Plasma layout did not complete: '+result.stdout+result.stderr)
        print(result.stdout.strip())
    run([qdbus(),'org.kde.KWin','/KWin','org.kde.KWin.reconfigure'],check=False)
    if shutil.which('gdbus'):
        run(['gdbus','call','--session','--dest','org.kde.kded6','--object-path','/kded','--method','org.kde.kded6.loadModule','appmenu'],check=False)

def system_call(action, assets, args, backup=None):
    cmd=[sys.executable,BASE/'startup.py',action,'--target-root',args.system_root]
    if action!='restore':
        cmd += ['--assets',assets/'system']
        if args.with_login: cmd += ['--login']
        if args.with_boot: cmd += ['--boot','--configure-initramfs']
    if backup: cmd += ['--backup',backup]
    if args.dry_run: cmd += ['--dry-run']
    if args.system_root=='/' and action in ('install','restore'): cmd=['sudo',*cmd]
    result=run(cmd,capture=True,check=False)
    print(result.stdout,flush=True)
    if result.returncode: raise RuntimeError(result.stderr.strip() or 'System theme preflight/installation failed.')
    return json.loads(result.stdout)

def aurorae_library():
    # Plasma 6.3 used the original factory name; newer versions also ship v2.
    roots=[Path('/usr/lib/qt6/plugins'),Path('/usr/lib64/qt6/plugins')]
    roots += list(Path('/usr/lib').glob('*/qt6/plugins'))
    if any(list(root.glob('org.kde.kdecoration*/org.kde.kwin.aurorae.v2.so')) for root in roots):
        return 'org.kde.kwin.aurorae.v2'
    return 'org.kde.kwin.aurorae'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--all',action='store_true',help='Desktop plus SDDM login and Plymouth boot theme.')
    p.add_argument('--with-login',action='store_true',help='Install matching SDDM theme, using sudo.')
    p.add_argument('--with-boot',action='store_true',help='Install Plymouth theme and rebuild initramfs, using sudo.')
    p.add_argument('--no-auto-align',action='store_true',help='Disable automatic widget repositioning after screen changes.')
    p.add_argument('--no-game-opacity',action='store_true',help='Keep the previous global translucency effect instead of game exemptions.')
    p.add_argument('--no-layout',action='store_true',help='Keep your existing panels/widgets; apply visual themes.')
    p.add_argument('--skip-deps',action='store_true',help='Use prerequisites already installed by you.')
    p.add_argument('--dry-run',action='store_true',help='Verify files and show plans without changing anything.')
    p.add_argument('--offline',action='store_true',help='Write theme settings without D-Bus or panel changes; useful from a text console.')
    p.add_argument('--restore',action='store_true',help='Restore the most recent desktop backup.')
    p.add_argument('--backup',type=Path,help='Restore a particular desktop backup.')
    p.add_argument('--restore-system',action='store_true',help='Also restore the startup backup linked to this desktop install.')
    p.add_argument('--home',help=argparse.SUPPRESS)
    p.add_argument('--system-root',default='/',help=argparse.SUPPRESS)
    args=p.parse_args()
    if args.all: args.with_login=args.with_boot=True
    if args.home and not (args.offline and args.skip_deps and args.no_layout): p.error('--home is an isolated test mode; it requires --offline --skip-deps --no-layout.')
    if args.home and (args.with_login or args.with_boot) and args.system_root=='/': p.error('An isolated home may not modify the running system startup themes.')
    if os.geteuid()==0 and not args.home: p.error('Run ./install.sh as your normal desktop user. Only package/startup steps use sudo.')
    if args.system_root!='/' and not args.home: p.error('--system-root is only for isolated tests with --home.')
    home=Home(args); manifest=verify()
    live=not args.offline
    if args.restore:
        backup=args.backup.resolve() if args.backup else home.backups/(home.backups/'latest').read_text().strip()
        meta=json.loads((backup/'backup.json').read_text())
        if args.dry_run: print('Would restore: '+str(backup)); return
        if args.restore_system:
            if not meta.get('startup_backup'): raise RuntimeError('This install did not record a startup-theme backup.')
            system_call('restore',None,args,meta['startup_backup'])
        if live: runtime_install.stop(sys.modules[__name__])
        mode=stop_shell() if live else None
        try: restore_files(home,backup)
        finally: start_shell(mode)
        if live:
            run([qdbus(),'org.kde.KWin','/KWin','org.kde.KWin.reconfigure'],check=False)
            if (home.config/'crimson-glass-runtime.json').exists() and (home.data/'crimson-glass/desktop_helper.py').exists():
                runtime_install.start(sys.modules[__name__],home)
        print('Restored previous desktop files. Log out and back in to reload application themes. Distribution packages were kept.')
        return
    if not args.home: plasma_check(live)
    if args.dry_run:
        if not args.skip_deps: dependencies.install(args.with_login,args.with_boot,dry_run=True)
        print('Would install Crimson Glass visual assets and back up existing files at '+str(home.backups))
        print('Layout: '+('keep current panels/widgets' if args.no_layout or args.offline else 'replace panels and primary-screen widgets with Crimson Glass'))
        print('Startup: '+('SDDM ' if args.with_login else '')+('Plymouth/initramfs' if args.with_boot else ''))
        return
    if not args.skip_deps: dependencies.install(args.with_login,args.with_boot)
    if not args.home: plasma_check(live)
    with tempfile.TemporaryDirectory(prefix='crimson-glass-') as temporary:
        assets=Path(temporary)
        print('Unpacking theme assets...',flush=True); extract_assets(assets)
        if args.with_login or args.with_boot: system_call('audit',assets,args)
        settings=json.loads((BASE/'settings.json').read_text())
        settings['kwinrc']['org.kde.kdecoration2']['library']=aurorae_library()
        settings['kdeglobals']['KDE']['LookAndFeelPackage']='org.crimsonglass.desktop'
        settings['kdeglobals'].pop('KDE-Global GUI Settings',None)
        if args.no_layout or args.offline:
            settings['dolphinrc'].pop('MainWindow',None)
        else:
            settings['konsolerc']['MainWindow']={'MenuBar':'Disabled'}
        items=destinations(assets,settings)
        backup,meta=snapshot(home,items)
        try:
            apply_assets(home,assets,items,register_launcher=live)
            # Keep selecting this global-theme preset compatible with the local
            # Aurorae factory when older Plasma 6 releases expose only that name.
            preset=home.data/'plasma/look-and-feel/org.crimsonglass.desktop/contents/defaults'
            ini_updates(preset,{'kwinrc][org.kde.kdecoration2':{
                'library':settings['kwinrc']['org.kde.kdecoration2']['library']}})
            for file,groups in settings.items(): ini_updates(home.config/file,groups)
            gtk_settings(home); configure_dolphin(home)
            runtime_install.setup(sys.modules[__name__],home,auto_align=not (args.no_auto_align or args.no_layout or args.offline),games=not args.no_game_opacity)
            if live:
                runtime_install.stop(sys.modules[__name__])
                live_apply(home,assets,not args.no_layout)
                runtime_install.start(sys.modules[__name__],home,register=not args.no_layout)
            if args.with_login or args.with_boot:
                report=system_call('install',assets,args)
                meta['startup_backup']=report['backup']
            meta['status']='installed'; atomic_write(backup/'backup.json',json.dumps(meta,indent=2)+'\n')
        except Exception:
            meta['status']='failed'; atomic_write(backup/'backup.json',json.dumps(meta,indent=2)+'\n')
            if not live:
                restore_files(home,backup); print('Failed install rolled back in isolated/offline home.',file=sys.stderr)
            else: print('Use ./restore.sh --backup '+shlex.quote(str(backup))+' to restore the saved desktop.',file=sys.stderr)
            raise
    print('Crimson Glass installed. Log out and back in to refresh all Qt/GTK applications and the global menu. Login/boot changes appear on the next login/boot; this script does not reboot.')

if __name__=='__main__':
    try: main()
    except (RuntimeError,OSError,ValueError,subprocess.CalledProcessError) as error:
        print('Crimson Glass: '+str(error),file=sys.stderr); sys.exit(1)
