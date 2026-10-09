"""Runtime regression tests without changing the host's displays or windows."""
import importlib.util, json, os, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('helper',ROOT/'runtime/desktop_helper.py'); helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
class Alignment(unittest.TestCase):
    def test_logical_resolutions(self):
        for width,height in [(1280,820),(1707,960),(1920,1080),(2560,1440),(3840,2160),(3440,1440)]:
            with self.subTest(size=(width,height)):
                rects=helper.positions(width,height)
                self.assertEqual(len(rects),5)
                for x,y,w,h in rects:self.assertTrue(x>=0 and y>=32 and x+w<=width and y+h<=height-68)
                self.assertEqual(rects[1][1],rects[2][1]); self.assertEqual(rects[0][0],rects[3][0]);self.assertEqual(rects[3][0],rects[4][0])
                for i,a in enumerate(rects):
                    for b in rects[i+1:]:self.assertTrue(a[0]+a[2]<=b[0] or b[0]+b[2]<=a[0] or a[1]+a[3]<=b[1] or b[1]+b[3]<=a[1])
    def test_preserves_unmanaged_and_old_screen(self):
        text='[Containments][12]\nItemGeometries-1707x960=Applet-1:1,2,3,4,0;Applet-99:10,20,30,40,0;\nItemGeometries-1920x1080=original;\nItemGeometriesHorizontal=Applet-99:1,2,3,4,0;\nfoo=bar\n[Other]\nx=42\n'
        out=helper.update_saved(text,12,1707,960,[1,2,3,4,5],helper.positions(1707,960),32)
        self.assertIn('Applet-99:10,20,30,40,0;',out);self.assertIn('ItemGeometries-1920x1080=original;',out);self.assertIn('[Other]\nx=42',out)
        self.assertEqual(out,helper.update_saved(out,12,1707,960,[1,2,3,4,5],helper.positions(1707,960),32))
    def test_disconnected_or_deleted_widgets(self):
        managed={'desktop':12,'widgets':[1,2,3,4,5]};self.assertIsNone(helper.signature({'desktops':[],'panels':[]},managed))
        snapshot={'desktops':[{'id':12,'screen':1,'geometry':{'width':1707,'height':960},'widgets':[{'id':i} for i in range(1,6)]}],'panels':[{'screen':1,'location':'top','height':32}]}
        self.assertEqual(helper.signature(snapshot,managed),(1,1707,960,32,0));snapshot['desktops'][0]['widgets'].pop();self.assertIsNone(helper.signature(snapshot,managed))
    def test_tiny_screen_rejected(self):
        with self.assertRaises(ValueError):helper.positions(1280,720)
class Detection(unittest.TestCase):
    def fixture(self,root,pid,environment,exe,parent=1):
        f=root/str(pid);f.mkdir();(f/'environ').write_bytes(environment);(f/'exe').symlink_to(exe);(f/'status').write_text(f'PPid:\t{parent}\n')
    def test_launch_sources_and_parent(self):
        for env in [b'SteamAppId=123\0',b'STEAM_COMPAT_APP_ID=45\0',b'LUTRIS_GAME_UUID=game\0',b'HEROIC_APP_NAME=game\0',b'CRIMSON_GLASS_GAME=1\0']:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);self.fixture(root,20,env,'/usr/bin/game');self.fixture(root,21,b'','/usr/bin/child',20);self.assertTrue(helper.process_is_game(21,root))
    def test_not_steam_launcher_or_terminal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root,20,b'SteamAppId=0\0','/usr/bin/steam');self.assertFalse(helper.process_is_game(20,root));self.assertFalse(helper.process_is_game(999,root))
    def test_native_steam_binary(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root,20,b'','/games/steamapps/common/Game/bin/game');self.assertTrue(helper.process_is_game(20,root))

class Opacity(unittest.TestCase):
    def test_window_lifecycle(self):
        from PyQt6.QtCore import QCoreApplication
        from PyQt6.QtQml import QJSEngine
        app=QCoreApplication.instance() or QCoreApplication([]); e=QJSEngine()
        mock='''var log=[],menu,added;function print(v){log.push(v);}function readConfig(k,d){return d;}
function Signal(){this.fs=[];this.connect=function(f){this.fs.push(f);};this.emit=function(){this.fs.slice().forEach(function(f){f();});};}
function Win(cls,pid,full){this.resourceClass=cls;this.pid=pid;this.fullScreen=!!full;this.normalWindow=true;this.dialog=false;this.active=true;this.opacity=1;this.internalId=cls+pid;['activeChanged','fullScreenChanged','windowClassChanged','opacityChanged','interactiveMoveResizeStarted','interactiveMoveResizeFinished','closed'].forEach(function(s){this[s]=new Signal();},this);}
var ordinary=new Win('kate',1),steam=new Win('steam_app_123',2),proton=new Win('game.exe',3),nativeGame=new Win('unknown-native-game',42),fullscreen=new Win('other-game',4,true),browser=new Win('browser',5);
var windows=[ordinary,steam,proton,nativeGame,fullscreen,browser];var workspace={windowAdded:new Signal(),windowList:function(){return windows;}};
function callDBus(service,path,iface,method,arg,callback){if(method==='IsGame')callback(arg===42);if(method==='GetClasses')arg('["remembered-game"]');}
function registerUserActionsMenu(f){menu=f;}
'''
        result=e.evaluate(mock+(ROOT/'runtime/game-opacity/contents/code/main.js').read_text());self.assertFalse(result.isError(),result.toString())
        result=e.evaluate("windows.forEach(function(w){w.active=false;w.activeChanged.emit();w.interactiveMoveResizeStarted.emit();});JSON.stringify(windows.map(function(w){return w.opacity;}));")
        self.assertEqual(json.loads(result.toString()),[.88,1,1,1,1,.88])
        self.assertEqual(e.evaluate('ordinary.interactiveMoveResizeFinished.emit();ordinary.opacity;').toNumber(),.97)
        self.assertEqual(e.evaluate('fullscreen.fullScreen=false;fullscreen.fullScreenChanged.emit();fullscreen.opacity;').toNumber(),.88)
        self.assertEqual(e.evaluate('browser.fullScreen=true;browser.fullScreenChanged.emit();browser.opacity;').toNumber(),1)
        self.assertEqual(e.evaluate('var n=new Win("remembered-game",7);workspace.windowAdded.emit=function(){this.fs.forEach(function(f){f(n);});};workspace.windowAdded.emit();n.active=false;n.activeChanged.emit();n.opacity;').toNumber(),1)
        self.assertEqual(e.evaluate('menu(ordinary).triggered();ordinary.opacity;').toNumber(),1)
        self.assertFalse(e.evaluate('nativeGame.closed.emit();nativeGame.activeChanged.emit();').isError())
class InstallerRuntime(unittest.TestCase):
    def test_migration_and_restore(self):
        import sys,types
        sys.path.insert(0,str(ROOT));import install,runtime_install
        with tempfile.TemporaryDirectory() as t:
            home=install.Home(types.SimpleNamespace(home=t));home.config.mkdir()
            original='[CrimsonGlass-Transparency]\nopacityactive=96\n[Personal]\nDescription=my own rule\n[General]\nrules=Personal,CrimsonGlass-Transparency\ncount=2\n'
            (home.config/'kwinrulesrc').write_text(original)
            (home.config/'kwinrc').write_text('[Personal]\nkeep=yes\n')
            backup,meta=install.snapshot(home,runtime_install.ITEMS+[('config','kwinrc')])
            runtime_install.setup(install,home)
            rules=(home.config/'kwinrulesrc').read_text();self.assertNotIn('[CrimsonGlass-Transparency]',rules);self.assertIn('Description=my own rule',rules);self.assertIn('rules=Personal',rules)
            self.assertTrue((home.data/'crimson-glass/desktop_helper.py').exists())
            self.assertIn('translucencyEnabled=false',(home.config/'kwinrc').read_text())
            runtime_install.setup(install,home)
            self.assertEqual(rules,(home.config/'kwinrulesrc').read_text())
            install.restore_files(home,backup)
            self.assertEqual((home.config/'kwinrulesrc').read_text(),original)
            self.assertEqual((home.config/'kwinrc').read_text(),'[Personal]\nkeep=yes\n')
            self.assertFalse((home.data/'crimson-glass').exists());self.assertFalse((home.config/'autostart/crimson-glass-runtime.desktop').exists())
if __name__=='__main__': unittest.main()
