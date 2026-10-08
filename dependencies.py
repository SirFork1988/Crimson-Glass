"""Native distribution packages; no third-party repositories or curl-to-shell."""
import os, re, shlex, shutil, subprocess
from pathlib import Path

RECIPES = {
 'arch': {
  'required': ['kvantum', 'kvantum-qt5', 'plasma-integration', 'plasma5-integration', 'breeze', 'breeze5', 'aurorae', 'qt6-5compat', 'kirigami-addons',
    'kde-gtk-config', 'kdeplasma-addons', 'plasma-systemmonitor', 'dolphin', 'konsole', 'ark',
    'kio-extras', 'ffmpegthumbs', 'kdegraphics-thumbnailers', 'qt6-svg', 'qt5-svg', 'qt6-tools',
    'gtk3', 'gtk4', 'noto-fonts', 'appmenu-gtk-module', 'libdbusmenu-glib'],
  'optional': ['xsettingsd', 'gtk-engine-murrine'],
  'login': ['sddm', 'qt6-5compat', 'qt6-virtualkeyboard', 'kirigami', 'qqc2-desktop-style'],
  'boot': ['plymouth'],
 },
 'debian': {
  'required': [['qt-style-kvantum', 'qt6-style-kvantum'], 'plasma-integration', 'plasma5-integration',
    ['kwin-style-aurorae', 'kwin-common'], 'qml6-module-qt5compat-graphicaleffects', 'qml6-module-org-kde-kirigamiaddons-components',
    ['kde-style-breeze', 'breeze'], 'kde-style-breeze-qt5', 'kde-config-gtk-style', 'plasma-widgets-addons',
    'plasma-systemmonitor', 'dolphin', 'konsole', 'ark', 'kio-extras', 'ffmpegthumbs', 'kdegraphics-thumbnailers',
    'libqt6svg6', ['libqt5svg5', 'libqt5svg5t64'], 'qdbus-qt6', ['libgtk-3-0t64','libgtk-3-0'], ['libgtk-4-1','libgtk-4-1t64'],
    'fonts-noto-core', 'fonts-noto-mono', 'appmenu-gtk3-module', ['libdbusmenu-glib4', 'libdbusmenu-glib4t64']],
  'optional': ['xsettingsd', 'gtk2-engines-murrine', 'appmenu-gtk2-module'],
  'login': ['sddm', 'sddm-theme-breeze', 'qml6-module-qt5compat-graphicaleffects',
    'qml6-module-qtquick-virtualkeyboard', 'qml6-module-org-kde-kirigami', 'qml6-module-org-kde-breeze',
    'qml6-module-qtquick-controls', 'qml6-module-qtquick-layouts'],
  'boot': ['plymouth', 'plymouth-themes'],
 },
 'fedora': {
  'required': [['kvantum','kvantum-qt6'], 'kvantum-qt5', 'plasma-integration', 'plasma-integration-qt5', 'aurorae', 'qt6-qt5compat', 'kf6-kirigami-addons',
    'plasma-breeze', 'plasma-breeze-qt5', 'kde-gtk-config', 'kdeplasma-addons', 'plasma-systemmonitor',
    'dolphin', 'konsole', 'ark', 'kio-extras', 'ffmpegthumbs', 'kdegraphics-thumbnailers',
    'qt6-qtsvg', 'qt5-qtsvg', ['qt6-qttools','qt6-qttools-tools'], 'gtk3', 'gtk4',
    'google-noto-sans-fonts', 'google-noto-sans-mono-fonts'],
  'optional': ['xsettingsd', 'appmenu-gtk-module', 'libdbusmenu-gtk3', 'gtk-murrine-engine'],
  'login': ['sddm', 'sddm-breeze', 'qt6-qt5compat', 'qt6-qtvirtualkeyboard', 'kf6-kirigami', 'kf6-qqc2-desktop-style'],
  'boot': ['plymouth', 'plymouth-plugin-two-step'],
 },
}

def run(args, **kwargs):
    return subprocess.run(args, text=True, **kwargs)

def distro():
    values={}
    for line in Path('/etc/os-release').read_text().splitlines():
        if '=' in line:
            k,v=line.split('=',1); values[k]=v.strip('"\'')
    ids=(values.get('ID','')+' '+values.get('ID_LIKE','')).split()
    if any(i in ids for i in ['arch','cachyos','manjaro','endeavouros']): return 'arch'
    if any(i in ids for i in ['debian','ubuntu','linuxmint','neon']): return 'debian'
    if any(i in ids for i in ['fedora']): return 'fedora'
    raise RuntimeError('Automatic dependencies support Arch/CachyOS, Debian/Ubuntu, and Fedora. Install the dependencies listed in README.txt and use --skip-deps on other Plasma 6 systems.')

def available(family, name):
    if family=='arch': return run(['pacman','-Si',name],capture_output=True).returncode==0
    if family=='debian':
        r=run(['apt-cache','policy',name],capture_output=True)
        return bool(re.search(r'Candidate:\s+(?!\(none\))\S+',r.stdout))
    r=run(['dnf','-q','repoquery','--available','--installed','--queryformat=%{name}',name],capture_output=True)
    return r.returncode==0 and name in r.stdout.split()

def plan(family, login=False, boot=False, query=True):
    recipe=RECIPES[family]
    groups=list(recipe['required'])+(recipe['login'] if login else [])+(recipe['boot'] if boot else [])
    selected=[]; missing=[]
    for group in groups:
        candidates=group if isinstance(group,list) else [group]
        found=next((p for p in candidates if not query or available(family,p)),None)
        if found: selected.append(found)
        else: missing.append('/'.join(candidates))
    optional=[p for p in recipe['optional'] if not query or available(family,p)]
    # Older Ubuntu Qt6 Kvantum packages split the Qt5 plugin; modern qt-style-kvantum carries both.
    if family=='debian' and 'qt-style-kvantum' not in selected:
        if not query or available(family,'qt5-style-kvantum'): selected.append('qt5-style-kvantum')
        else: missing.append('Qt5 Kvantum plugin (qt5-style-kvantum)')
    if missing: raise RuntimeError('Required packages unavailable in enabled repositories: '+', '.join(missing)+'. Enable the distro’s standard KDE/universe repositories or install the corresponding packages, then use --skip-deps. No desktop settings were changed.')
    return list(dict.fromkeys(selected+optional))

def install(login=False, boot=False, dry_run=False):
    family=distro()
    if dry_run:
        packages=plan(family,login,boot,query=False)
        print('Dependency plan ('+family+'): '+', '.join(packages)); return family
    sudo=[] if os.geteuid()==0 else ['sudo']
    if sudo and not shutil.which('sudo'): raise RuntimeError('sudo is required to install distribution packages.')
    if family=='debian':
        run(sudo+['apt-get','update'],check=True)
    packages=plan(family,login,boot)
    if family=='arch': cmd=['pacman','-S','--needed']+packages
    elif family=='debian': cmd=['apt-get','install','--no-remove']+packages
    else: cmd=['dnf','install']+packages
    print('Installing prerequisites: '+shlex.join(cmd),flush=True)
    run(sudo+cmd,check=True)
    return family
