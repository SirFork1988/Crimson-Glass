/* SPDX-License-Identifier: MIT */
(function () {
    var records = [], extra = String(readConfig("OpaqueClasses", "")).toLowerCase().split(",");
    function gameClass(w) {
        var cls = String(w.resourceClass || "").toLowerCase();
        return w.caption === "ProjectM Display Mirror" || /^steam_app_\d+$/.test(cls) || /\.exe$/.test(cls) ||
            /^(projectm|projectm-pulseaudio|projectmsdl|projectm-sdl|gamescope|retroarch|rpcs3|pcsx2|dolphin-emu|org\.dolphinemu\.dolphin-emu|minecraft|lutris|heroic|bottles)$/.test(cls) ||
            extra.some(function (c) { return c.trim() && c.trim() === cls; });
    }
    function update(r) {
        var w=r.window;
        if (r.closed || w.deleted || !w.normalWindow && !w.dialog) return;
        var exempt=w.fullScreen || r.processGame || gameClass(w);
        var target=exempt ? 1 : Math.min(r.original,w.active ? (w.dialog ? 0.96 : 1) : 0.97);
        if (!exempt && r.moving) target=Math.min(target,0.88);
        if (Math.abs(w.opacity-target)>0.001) { r.writing=true; w.opacity=target; r.writing=false; }
    }
    function attach(w) {
        if (!w.normalWindow && !w.dialog || w.deleted) return;
        var r={window:w, original:w.opacity,processGame:false,closed:false,moving:false,writing:false};records.push(r);
        function refresh() { update(r); }
        w.activeChanged.connect(refresh); w.fullScreenChanged.connect(refresh); w.windowClassChanged.connect(refresh);
        w.opacityChanged.connect(function(){if (!r.writing) update(r);});
        w.interactiveMoveResizeStarted.connect(function(){r.moving=true;update(r);});
        w.interactiveMoveResizeFinished.connect(function(){r.moving=false;update(r);});
        callDBus("org.crimsonglass.Desktop","/Desktop","org.crimsonglass.Desktop","Original",String(w.internalId),Number(r.original));
        w.closed.connect(function(){callDBus("org.crimsonglass.Desktop","/Desktop","org.crimsonglass.Desktop","Forget",String(w.internalId));r.closed=true;var i=records.indexOf(r);if(i>=0)records.splice(i,1);});
        update(r);
        if (w.pid>0) callDBus("org.crimsonglass.Desktop","/Desktop","org.crimsonglass.Desktop","IsGame",w.pid,function(isGame){if(!r.closed){r.processGame=isGame===true;update(r);}});
    }
    // A launch-source-independent escape hatch for unusual native windowed games.
    registerUserActionsMenu(function(w){return {title:"Crimson Glass: keep this window opaque",triggered:function(){var cls=String(w.resourceClass||"").toLowerCase();if(extra.indexOf(cls)<0)extra.push(cls);records.forEach(function(r){if(r.window===w){r.processGame=true;update(r);}});callDBus("org.crimsonglass.Desktop","/Desktop","org.crimsonglass.Desktop","RememberClass",cls);}};});
    workspace.windowAdded.connect(attach);workspace.windowList().forEach(attach);
    callDBus("org.crimsonglass.Desktop","/Desktop","org.crimsonglass.Desktop","GetClasses",function(value){try{JSON.parse(value).forEach(function(cls){if(extra.indexOf(cls)<0)extra.push(cls);});records.forEach(update);}catch(e){print("Crimson Glass: could not read opaque class preferences");}});
}());
