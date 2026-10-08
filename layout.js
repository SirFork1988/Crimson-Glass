/* SPDX-License-Identifier: MIT
 * Crimson Glass portable Plasma 6 layout.
 * Installer must back up plasma-org.kde.plasma.desktop-appletsrc first.
 * --no-layout must skip evaluating this file. Applying replaces every panel
 * and the current primary-screen desktop widgets; other desktops remain.
 * Replace __WALLPAPER_URI__ with an escaped file URI at install time.
 * Optionally prepend var crimsonLayoutOptions = {rootDiskSensorPrefix: ...};
 * Discover that prefix on the destination host; never copy a disk UUID.
 */
(function () {
    var options = typeof crimsonLayoutOptions === "object" ? crimsonLayoutOptions : {};
    var screenIndex = 0; // Plasma's primary screen, queried at execution time.
    var geo = screenGeometry(screenIndex);
    if (!geo || geo.width <= 0 || geo.height <= 0) {
        throw new Error("No primary Plasma screen is available.");
    }
    var wallpaperUri = "__WALLPAPER_URI__";
    if (wallpaperUri.indexOf("__WALLPAPER_") === 0) {
        throw new Error("Installer has not supplied the wallpaper URI.");
    }
    var required = [
        "com.github.SnoutBug.mmckLauncher", "org.kde.plasma.appmenu",
        "org.kde.plasma.panelspacer", "org.kde.plasma.pager",
        "org.kde.plasma.systemtray", "org.kde.plasma.digitalclock",
        "org.kde.plasma.icontasks", "org.kde.plasma.trash",
        "org.kde.plasma.systemmonitor.cpu", "org.kde.plasma.systemmonitor.memory",
        "org.kde.plasma.systemmonitor.net", "org.kde.plasma.systemmonitor.diskusage"
    ];
    required.forEach(function (id) {
        if (knownWidgetTypes.indexOf(id) < 0) {
            throw new Error("Required Plasma widget is unavailable: " + id);
        }
    });
    var candidates = [
        "org.kde.dolphin.desktop", "org.kde.konsole.desktop", "org.kde.kate.desktop",
        "org.kde.gwenview.desktop", "org.kde.haruna.desktop", "org.kde.spectacle.desktop",
        "org.kde.plasma-systemmonitor.desktop", "systemsettings.desktop"
    ];
    var dockApps = candidates.filter(function (id) { return applicationExists(id); })
        .map(function (id) { return "applications:" + id; });
    if (!dockApps.length) {
        throw new Error("Install Dolphin or another KDE desktop application before applying this layout.");
    }
    var desktop = desktopForScreen(screenIndex);
    if (!desktop) {
        throw new Error("The primary-screen desktop is unavailable.");
    }
    // All validation above is read-only. The installer has already saved the old layout.
    panels().forEach(function (panel) { panel.remove(); });
    desktop.widgets().forEach(function (widget) { widget.remove(); });

    function write(widget, group, values) {
        widget.currentConfigGroup = group;
        Object.keys(values).forEach(function (key) { widget.writeConfig(key, values[key]); });
    }
    function finish(widget) {
        widget.currentConfigGroup = [];
        widget.reloadConfig();
        return widget;
    }
    var top = new Panel;
    top.screen = screenIndex;
    top.location = "top";
    top.height = Math.round(gridUnit * 16 / 9);
    top.lengthMode = "fill";
    top.alignment = "center";
    top.floating = false;
    top.opacity = "translucent";
    top.hiding = "none";
    var launcher = top.addWidget("com.github.SnoutBug.mmckLauncher");
    write(launcher, ["General"], {
        icon: "start-here-kde", useCustomButtonImage: false,
        enableGreeting: true, floating: true, indicatorColor: "#e84156",
        launcherPosition: 0, numberColumns: 6, numberOfRows: 3,
        showItemsInGrid: true, useSystemFontSettings: true,
        favoriteApps: dockApps, favoriteSystemActions: [], favoritesPortedToKAstats: false
    });
    launcher.globalShortcut = "Alt+F1";
    finish(launcher);
    top.addWidget("org.kde.plasma.appmenu");
    top.addWidget("org.kde.plasma.panelspacer");
    top.addWidget("org.kde.plasma.pager");
    top.addWidget("org.kde.plasma.systemtray");
    var clock = top.addWidget("org.kde.plasma.digitalclock");
    write(clock, ["Appearance"], {
        showDate: true, dateFormat: "custom", customDateFormat: "ddd, MMM d", use24hFormat: 0
    });
    finish(clock);

    var dock = new Panel;
    dock.screen = screenIndex;
    dock.location = "bottom";
    dock.height = Math.round(gridUnit * 34 / 9);
    dock.lengthMode = "fit";
    dock.alignment = "center";
    dock.floating = true;
    dock.opacity = "translucent";
    dock.hiding = "dodgewindows";
    var tasks = dock.addWidget("org.kde.plasma.icontasks");
    write(tasks, ["General"], {
        launchers: dockApps, showOnlyCurrentDesktop: false, showToolTips: true
    });
    finish(tasks);
    dock.addWidget("org.kde.plasma.trash");

    desktop.wallpaperPlugin = "org.kde.image";
    write(desktop, ["Wallpaper", "org.kde.image", "General"], {Image: wallpaperUri});
    finish(desktop);

    // Widget positions use local desktop coordinates and current logical screen dimensions.
    var margin = Math.max(12, Math.min(40, Math.round(geo.width / 60)));
    var availableHeight = Math.max(160, geo.height - top.height - dock.height - 3 * margin);
    var scale = Math.min(1.5, geo.width / 1920, availableHeight / 816);
    var width = Math.round(464 * scale);
    var gap = Math.max(8, Math.round(32 * scale));
    var halfWidth = Math.floor((width - gap) / 2);
    var x = Math.max(margin, geo.width - margin - width);
    var y = top.height + Math.round(margin / 2);
    var clockHeight = Math.round(144 * scale);
    var pieHeight = Math.round(224 * scale);
    var netHeight = Math.round(192 * scale);
    var diskHeight = Math.round(160 * scale);
    var desktopClock = desktop.addWidget("org.kde.plasma.digitalclock", x, y, width, clockHeight);
    write(desktopClock, ["Appearance"], {
        showDate: true, dateFormat: "custom", customDateFormat: "dddd, MMMM d", use24hFormat: 0
    });
    finish(desktopClock);
    y += clockHeight + gap;

    function monitor(plugin, title, face, px, py, pw, ph, high, low, total, colors) {
        var widget = desktop.addWidget(plugin, px, py, pw, ph);
        write(widget, [], {CurrentPreset: "org.kde.plasma.systemmonitor", UserBackgroundHints: "NoBackground"});
        write(widget, ["Appearance"], {title: title, chartFace: face});
        write(widget, ["Sensors"], {
            highPrioritySensorIds: JSON.stringify(high),
            lowPrioritySensorIds: JSON.stringify(low), totalSensors: JSON.stringify(total)
        });
        write(widget, ["SensorColors"], colors);
        return finish(widget);
    }
    var cpu = monitor("org.kde.plasma.systemmonitor.cpu", "CPU", "org.kde.ksysguard.piechart",
        x, y, halfWidth, pieHeight, ["cpu/all/usage"], [], ["cpu/all/usage"], {"cpu/all/usage": "232,65,86"});
    var memory = monitor("org.kde.plasma.systemmonitor.memory", "MEMORY", "org.kde.ksysguard.piechart",
        x + halfWidth + gap, y, halfWidth, pieHeight, ["memory/physical/used"], [],
        ["memory/physical/usedPercent"], {"memory/physical/used": "255,131,148", "memory/physical/usedPercent": "255,131,148"});
    y += pieHeight + gap;
    var network = monitor("org.kde.plasma.systemmonitor.net", "NETWORK", "org.kde.ksysguard.linechart",
        x, y, width, netHeight, ["network/all/download", "network/all/upload"], [], [],
        {"network/all/download": "232,65,86", "network/all/upload": "246,183,193"});
    y += netHeight + gap;
    // The destination installer can resolve disk/<root filesystem UUID> using findmnt
    // and verify the resulting sensor via org.kde.ksystemstats1.sensors(). Otherwise
    // use ksystemstats' portable aggregate, accurately titled STORAGE.
    var diskPrefix = typeof options.rootDiskSensorPrefix === "string" &&
        /^disk\/[A-Za-z0-9._-]+$/.test(options.rootDiskSensorPrefix)
        ? options.rootDiskSensorPrefix : "disk/all";
    var diskColors = {};
    diskColors[diskPrefix + "/usedPercent"] = "232,65,86";
    var disk = monitor("org.kde.plasma.systemmonitor.diskusage",
        diskPrefix === "disk/all" ? "STORAGE" : "STORAGE · /", "org.kde.ksysguard.horizontalbars",
        x, y, width, diskHeight, [diskPrefix + "/usedPercent"], [diskPrefix + "/free", diskPrefix + "/total"], [], diskColors);
    print(JSON.stringify({layout: "Crimson Glass", screen: screenIndex, topPanel: top.id,
        dockPanel: dock.id, monitorWidgets: [desktopClock.id, cpu.id, memory.id, network.id, disk.id],
        diskSensorPrefix: diskPrefix, dockApplications: dockApps}));
}());
