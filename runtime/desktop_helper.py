#!/usr/bin/env python3
"""Crimson Glass screen alignment and game detection; user-session only."""
# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse, json, os, re, shutil, subprocess, tempfile, time

SERVICE='org.crimsonglass.Desktop'
INTERFACE=SERVICE
TYPES=['org.kde.plasma.digitalclock','org.kde.plasma.systemmonitor.cpu','org.kde.plasma.systemmonitor.memory','org.kde.plasma.systemmonitor.net','org.kde.plasma.systemmonitor.diskusage']

def roots():
    home=Path.home()
    return (Path(os.environ.get('XDG_CONFIG_HOME',home/'.config')), Path(os.environ.get('XDG_DATA_HOME',home/'.local/share')), Path(os.environ.get('XDG_STATE_HOME',home/'.local/state')))

def atomic(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    mode=path.stat().st_mode&0o777 if path.exists() else 0o600
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as f:
        f.write(text); temp=Path(f.name)
    temp.chmod(mode); os.replace(temp,path)

def positions(width,height,top=32,dock=68):
    # Plasma's logical pixels, never physical 4K pixels. Snap to a 16-pixel grid.
    if width<800 or height<816: raise ValueError('Screen too small for five monitoring widgets')
    snap=lambda v:max(16,round(v/16)*16)
    margin=32; gap=16
    scale=min(1.5,width/1920,(height-top-dock-64)/768)
    w=max(464,snap(464*scale)); half=(w-gap)//2
    heights=[max(minimum,snap(n*scale)) for n,minimum in zip((144,224,192,160),(128,224,144,144))]
    while sum(heights)+3*gap+snap(top+16)>height-dock:
        candidates=[i for i,(h,minimum) in enumerate(zip(heights,(128,224,144,144))) if h>minimum]
        if not candidates: raise ValueError('Screen too small for legible monitoring widgets')
        heights[max(candidates,key=lambda i:heights[i])]-=16
    x=(width-margin-w)//16*16; y=snap(top+16)
    result=[[x,y,w,heights[0]]]; y+=heights[0]+gap
    result += [[x,y,half,heights[1]],[x+half+gap,y,w-half-gap,heights[1]]]; y+=heights[1]+gap
    result.append([x,y,w,heights[2]]); y+=heights[2]+gap
    result.append([x,y,w,heights[3]])
    if any(x<0 or y<top or x+w>width or y+h>height-dock for x,y,w,h in result): raise ValueError('Widget layout would leave available desktop')
    return result

PROBE='''print(JSON.stringify({desktops:desktops().filter(function(d){return d.screen>=0;}).map(function(d){return {id:d.id,screen:d.screen,geometry:screenGeometry(d.screen),widgets:d.widgets().map(function(w){return {id:w.id,type:w.type,geometry:w.geometry};})};}),panels:panels().map(function(p){return {screen:p.screen,location:p.location,height:p.height};})}));'''
def probe():
    q=shutil.which('qdbus6') or shutil.which('qdbus-qt6')
    if not q: raise RuntimeError('Qt 6 qdbus is required')
    r=subprocess.run([q,'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',PROBE],text=True,capture_output=True,timeout=10,check=True)
    return json.loads(r.stdout)

def signature(snapshot,managed):
    for d in snapshot['desktops']:
        if d['id']==managed['desktop'] and all(any(w['id']==wid for w in d['widgets']) for wid in managed['widgets']):
            g=d['geometry']; ps=[p for p in snapshot['panels'] if p['screen']==d['screen']]
            return (d['screen'],g['width'],g['height'],max([p['height'] for p in ps if p['location']=='top'] or [0]),max([p['height'] for p in ps if p['location']=='bottom'] or [0]))
    return None

def update_saved(text,desktop,width,height,ids,rects,top):
    header=f'[Containments][{int(desktop)}]'
    lines=text.splitlines(keepends=True); start=next(i for i,l in enumerate(lines) if l.strip()==header)+1
    end=next((i for i in range(start,len(lines)) if lines[i].startswith('[')),len(lines))
    section=''.join(lines[start:end]); replacement={str(i):f'Applet-{i}:{x},{y-top},{w},{h},0;' for i,(x,y,w,h) in zip(ids,rects)}
    for key in (f'ItemGeometries-{width}x{height}','ItemGeometriesHorizontal'):
        match=re.search(r'^'+re.escape(key)+r'=(.*)$',section,re.M)
        old=match.group(1) if match else ''
        # Other widgets and other screen-size layouts are preserved.
        other=''.join(part+';' for part in old.split(';') if part and not re.match(r'Applet-('+ '|'.join(re.escape(str(i)) for i in ids)+r'):',part))
        value=key+'='+other+''.join(replacement.values())+'\n'
        if match: section=section[:match.start()]+value+section[match.end():].lstrip('\n')
        else: section+=value
    return ''.join(lines[:start])+section+''.join(lines[end:])

def align(managed,expected,config,state):
    if signature(probe(),managed)!=expected: return False
    screen,width,height,top,dock=expected
    rects=positions(width,height,top,dock)
    mode=None
    try:
        if shutil.which('systemctl') and subprocess.run(['systemctl','--user','is-active','--quiet','plasma-plasmashell.service']).returncode==0:
            mode='systemd'
            subprocess.run(['systemctl','--user','stop','plasma-plasmashell.service'],check=True,timeout=20)
        else:
            mode='manual'
            subprocess.run(['kquitapp6','plasmashell'],check=True,timeout=20)
        path=config/'plasma-org.kde.plasma.desktop-appletsrc'
        old=path.read_text()
        backup=state/'crimson-glass/alignment-backups'/str(time.time_ns())
        atomic(backup,old)
        # Keep the last five automatic layout backups.
        for stale in sorted(backup.parent.iterdir())[:-5]: stale.unlink()
        atomic(path,update_saved(old,managed['desktop'],width,height,managed['widgets'],rects,top))
    finally:
        if mode=='systemd': subprocess.run(['systemctl','--user','start','plasma-plasmashell.service'],check=True,timeout=20)
        elif mode=='manual': subprocess.Popen(['plasmashell'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    print(f'Crimson Glass: aligned widgets for {width}x{height} logical pixels',flush=True)
    return True

def process_is_game(pid,proc=Path('/proc')):
    # No environment values are logged, stored, or sent outside this process.
    for _ in range(8):
        if pid<=1: break
        folder=proc/str(pid)
        try:
            if folder.stat().st_uid!=os.getuid(): return False
            env=dict(item.split(b'=',1) for item in (folder/'environ').read_bytes()[:262144].split(b'\0') if b'=' in item)
            if any(env.get(k,b'') not in (b'',b'0') for k in (b'SteamAppId',b'SteamGameId',b'STEAM_COMPAT_APP_ID',b'LUTRIS_GAME_UUID',b'HEROIC_APP_NAME',b'CRIMSON_GLASS_GAME')): return True
            exe=os.readlink(folder/'exe').lower()
            if any(part in exe for part in ('/steamapps/common/','/gog games/')): return True
            status=(folder/'status').read_text(); pid=int(re.search(r'^PPid:\s*(\d+)',status,re.M).group(1))
        except (OSError,ValueError,AttributeError): return False
    return False

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--once',action='store_true'); parser.add_argument('--register',action='store_true'); args=parser.parse_args()
    config,data,state=roots(); settings_path=config/'crimson-glass-runtime.json'
    settings=json.loads(settings_path.read_text())
    if args.register:
        d=next(d for d in probe()['desktops'] if d['screen']==0)
        groups=[[w['id'] for w in d['widgets'] if w['type']==kind] for kind in TYPES]
        if not all(len(g)==1 for g in groups): raise RuntimeError('Expected exactly one of each Crimson Glass monitoring widget')
        settings['managed']={'desktop':d['id'],'widgets':[g[0] for g in groups]}; settings['last_screen']=signature(probe(),settings['managed']); atomic(settings_path,json.dumps(settings,indent=2)+'\n'); return
    if args.once:
        managed=settings.get('managed'); sig=signature(probe(),managed) if managed else None
        if sig:
            try: align(managed,sig,config,state)
            except ValueError as e: print('Crimson Glass alignment: '+str(e),flush=True)
        return
    import dbus, dbus.service
    from dbus.mainloop.glib import DBusGMainLoop
    from gi.repository import GLib
    DBusGMainLoop(set_as_default=True); bus=dbus.SessionBus(); name=dbus.service.BusName(SERVICE,bus=bus,do_not_queue=True)
    loop=GLib.MainLoop(); originals={}
    class Detector(dbus.service.Object):
        @dbus.service.method(INTERFACE,in_signature='i',out_signature='b')
        def IsGame(self,pid): return bool(settings.get('game_opacity',True) and process_is_game(int(pid)))
        @dbus.service.method(INTERFACE,in_signature='',out_signature='s')
        def GetClasses(self): return json.dumps(settings.get('opaque_classes',[]))
        @dbus.service.method(INTERFACE,in_signature='s',out_signature='')
        def RememberClass(self,cls):
            cls=str(cls).lower().strip()
            if not cls or len(cls)>256 or any(ord(c)<32 for c in cls): return
            classes=settings.setdefault('opaque_classes',[])
            if cls not in classes: classes.append(cls); atomic(settings_path,json.dumps(settings,indent=2)+'\n')
        @dbus.service.method(INTERFACE,in_signature='sd',out_signature='')
        def Original(self,key,value):
            if len(originals)<4096: originals.setdefault(str(key),max(0,min(1,float(value))))
        @dbus.service.method(INTERFACE,in_signature='s',out_signature='')
        def Forget(self,key): originals.pop(str(key),None)
        @dbus.service.method(INTERFACE,in_signature='',out_signature='')
        def Quit(self): loop.quit()
    detector=Detector(name,'/Desktop')
    q=shutil.which('qdbus6') or shutil.which('qdbus-qt6')
    def kwin(method,*args):
        return subprocess.run([q,'org.kde.KWin','/Scripting','org.kde.kwin.Scripting.'+method,*args],capture_output=True,text=True,timeout=10,check=True)
    plugin='crimson-glass-game-opacity'
    if settings.get('game_opacity',True):
        kwin('unloadScript',plugin)
        kwin('loadScript',str(data/'kwin/scripts'/plugin/'contents/code/main.js'),plugin)
        kwin('start')
    previous=tuple(settings['last_screen']) if settings.get('last_screen') else None; pending=None; stable=0; last_restart=0
    def tick():
        nonlocal previous,pending,stable,last_restart
        try:
            managed=settings.get('managed')
            if not settings.get('auto_align',True) or not managed: return True
            snap=probe(); sig=signature(snap,managed)
            if sig is None: return True
            if previous is None: previous=sig; return True # Leave manual positioning alone on ordinary login.
            if sig==previous: pending=None; stable=0; return True
            if sig!=pending: pending=sig; stable=1; return True
            stable+=1
            if stable>=3 and time.monotonic()-last_restart>30:
                if align(managed,sig,config,state):
                    previous=sig; last_restart=time.monotonic(); pending=None; stable=0
                    settings['last_screen']=sig; atomic(settings_path,json.dumps(settings,indent=2)+'\n')
        except ValueError as e:
            previous=pending;pending=None;stable=0;print('Crimson Glass alignment: '+str(e),flush=True)
        except (OSError,RuntimeError,StopIteration,subprocess.SubprocessError) as e: print('Crimson Glass alignment: '+str(e),flush=True)
        return True
    GLib.timeout_add_seconds(3,tick)
    try: loop.run()
    finally:
        if settings.get('game_opacity',True):
            kwin('unloadScript',plugin)
            # Restore only windows this script actually observed, not unrelated rules.
            cleanup='var originals='+json.dumps(originals)+';workspace.windowList().forEach(function(w){var id=String(w.internalId);if(Object.prototype.hasOwnProperty.call(originals,id))w.opacity=originals[id];});'
            path=state/'crimson-glass/opacity-cleanup.js';atomic(path,cleanup)
            kwin('unloadScript',plugin+'-cleanup');kwin('loadScript',str(path),plugin+'-cleanup');kwin('start')


if __name__=='__main__': main()
