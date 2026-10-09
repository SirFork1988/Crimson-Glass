/* SPDX-License-Identifier: MIT
 * Crimson Glass native Plasma 6 desktop layout.
 * Offered through the Global Theme "desktop layout" choice. Plasma owns the
 * user-requested layout reset; there are no shell commands or removals here.
 * A display watcher/game policy is available separately in the full installer.
 */
(function () {
    var screenIndex = 0; // Plasma's primary screen, queried at execution time.
    var geo = screenGeometry(screenIndex);
    if (!geo || geo.width <= 0 || geo.height <= 0) {
        throw new Error("No primary Plasma screen is available.");
    }
    var required = [
        "org.kde.plasma.appmenu",
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
    // KDE runs this only when the user selects the global theme desktop layout.
    // KDE owns its reset operation; this script never deletes panels or widgets.

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
    var launcherType = knownWidgetTypes.indexOf("com.github.SnoutBug.mmckLauncher") >= 0
        ? "com.github.SnoutBug.mmckLauncher" : "org.kde.plasma.kickoff";
    var launcher = top.addWidget(launcherType);
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
    finish(desktop);

    // Work in current logical pixels, including HiDPI scaling. Native Store
    // installation sets positions once; the full installer adds display watching.
    var scale = Math.min(1.5, Math.max(1, geo.width / 1920));
    function grid(value) { return Math.ceil(value / 16) * 16; }
    var width = grid(464 * scale);
    var gap = 16;
    var halfWidth = (width - gap) / 2;
    var margin = 32;
    var x = Math.floor((geo.width - width - margin) / 16) * 16;
    var y = grid(top.height + 16);
    var clockHeight = grid(128 * scale);
    var pieHeight = grid(224 * scale);
    var netHeight = grid(176 * scale);
    var diskHeight = grid(144 * scale);
    var minimums = [128, 224, 144, 144];
    var heights = [clockHeight, pieHeight, netHeight, diskHeight];
    var room = geo.height - y - dock.height - 32 - 3 * gap;
    while (heights.reduce(function (sum, h) { return sum + h; }, 0) > room) {
        var reduced = false;
        for (var row = 3; row >= 0; row--) {
            if (heights[row] > minimums[row]) {
                heights[row] -= 16;
                reduced = true;
                break;
            }
        }
        if (!reduced) {
            print("Crimson Glass: display is too small for the five desktop monitors; panels installed.");
            return;
        }
    }
    if (x < margin || geo.width < 800) {
        print("Crimson Glass: display is too narrow for the desktop monitors; panels installed.");
        return;
    }
    clockHeight = heights[0]; pieHeight = heights[1];
    netHeight = heights[2]; diskHeight = heights[3];
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
    // No destination-specific disk UUIDs are embedded in the Store package.
    var diskPrefix = "disk/all";
    var diskColors = {};
    diskColors[diskPrefix + "/usedPercent"] = "232,65,86";
    var disk = monitor("org.kde.plasma.systemmonitor.diskusage",
        diskPrefix === "disk/all" ? "STORAGE" : "STORAGE · /", "org.kde.ksysguard.horizontalbars",
        x, y, width, diskHeight, [diskPrefix + "/usedPercent"], [diskPrefix + "/free", diskPrefix + "/total"], [], diskColors);
    print(JSON.stringify({layout: "Crimson Glass", screen: screenIndex, topPanel: top.id,
        dockPanel: dock.id, monitorWidgets: [desktopClock.id, cpu.id, memory.id, network.id, disk.id],
        diskSensorPrefix: diskPrefix, dockApplications: dockApps}));
}());
