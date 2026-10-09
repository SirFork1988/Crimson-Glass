"""Install backed-up Crimson Glass runtime helpers without replacing panels."""
# SPDX-License-Identifier: MIT
import json, shlex, shutil, subprocess, sys
from pathlib import Path

ITEMS=[('data','crimson-glass'),('data','kwin/scripts/crimson-glass-game-opacity'),('config','autostart/crimson-glass-runtime.desktop'),('config','crimson-glass-runtime.json'),('config','kwinrulesrc')]

def setup(installer,home,auto_align=True,games=True):
    root=home.data/'crimson-glass';root.mkdir(parents=True,exist_ok=True)
    shutil.copy2(installer.BASE/'runtime/desktop_helper.py',root/'desktop_helper.py')
    target=home.data/'kwin/scripts/crimson-glass-game-opacity'
    installer.remove(target);shutil.copytree(installer.BASE/'runtime/game-opacity',target)
    conf=home.config/'crimson-glass-runtime.json'
    previous=json.loads(conf.read_text()) if conf.exists() else {}
    previous.update(auto_align=auto_align,game_opacity=games)
    installer.atomic_write(conf,json.dumps(previous,indent=2)+'\n')
    def desktop_quote(value): return '"'+str(value).replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')+'"'
    installer.atomic_write(home.config/'autostart/crimson-glass-runtime.desktop',
        '[Desktop Entry]\nType=Application\nName=Crimson Glass desktop helper\nComment=Screen-aware monitoring widgets and opaque games\nExec='+desktop_quote(sys.executable)+' '+desktop_quote(root/'desktop_helper.py')+'\nOnlyShowIn=KDE;\nX-KDE-autostart-after=panel\nTerminal=false\n')
    # The broad effect cannot exclude games. Its desktop-window fading is replaced
    # by the bundled KWin script; application-owned alpha/blur is left intact.
    installer.ini_updates(home.config/'kwinrc',{'Plugins':{'translucencyEnabled':'false' if games else 'true',**({'translucency-projectm-exemptEnabled':'false'} if games else {}),'crimson-glass-game-opacityEnabled':'true' if games else 'false'}})

    if games:
        # Migrate only the old Crimson Glass catch-all opacity rule. User rules stay.
        rules=home.config/'kwinrulesrc'
        if rules.exists():
            import configparser, re
            text=rules.read_text(); old=configparser.ConfigParser(interpolation=None,strict=False);old.read_string(text)
            ids=[x for x in old.get('General','rules',fallback='').split(',') if x and x!='CrimsonGlass-Transparency']
            text=re.sub(r'(?ms)^\[CrimsonGlass-Transparency\]\n.*?(?=^\[|\Z)','',text)
            installer.atomic_write(rules,text)
            installer.ini_updates(rules,{'General':{'rules':','.join(ids),'count':len(ids)}})

def stop(installer):
    q=installer.qdbus()
    installer.run([q,'org.crimsonglass.Desktop','/Desktop','org.crimsonglass.Desktop.Quit'],check=False,capture=True)
    import time
    for _ in range(30):
        status=installer.run([q,'org.crimsonglass.Desktop','/Desktop','org.freedesktop.DBus.Peer.Ping'],check=False,capture=True)
        if status.returncode: break
        time.sleep(0.1)
    installer.run([q,'org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript','crimson-glass-game-opacity'],check=False,capture=True)

def start(installer,home,register=False):
    helper=home.data/'crimson-glass/desktop_helper.py'
    if register:
        installer.run([sys.executable,helper,'--register'])
        settings=json.loads((home.config/'crimson-glass-runtime.json').read_text())
        if settings.get('auto_align',True): installer.run([sys.executable,helper,'--once'])
    log=home.state/'crimson-glass/runtime.log';log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('a') as f:
        process=subprocess.Popen([sys.executable,helper],stdout=f,stderr=f,start_new_session=True)
    import time
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        if process.poll() is not None: raise RuntimeError('Crimson Glass helper failed to start; see '+str(log))
        status=installer.run([installer.qdbus(),'org.crimsonglass.Desktop','/Desktop','org.crimsonglass.Desktop.GetClasses'],check=False,capture=True)
        if status.returncode==0: return
        time.sleep(0.2)
    process.terminate();raise RuntimeError('Crimson Glass helper did not become ready; see '+str(log))
