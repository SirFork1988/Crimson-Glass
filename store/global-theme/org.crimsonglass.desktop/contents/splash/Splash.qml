// SPDX-License-Identifier: CC0-1.0
import QtQuick

Rectangle {
    id: root
    color: "#08090c"

    // KSplash supplies real startup stages, from 0 through 6.
    property int stage: 0
    readonly property real progress: Math.max(0, Math.min(1, stage / 6))
    readonly property real unitScale: Math.max(0.75, Math.min(1.35, height / 1080))
    readonly property bool finished: stage >= 6

    Image {
        anchors.fill: parent
        source: "images/background.png"
        fillMode: Image.PreserveAspectCrop
        opacity: 0.55
    }

    Rectangle {
        anchors.fill: parent
        color: "#08090c"
        opacity: 0.37
    }

    Item {
        id: entrance
        anchors.fill: parent
        opacity: 0
        Component.onCompleted: appear.start()

        Image {
            id: mark
            anchors.horizontalCenter: parent.horizontalCenter
            y: root.height * 0.45 - height / 2
            width: 128 * root.unitScale
            height: width
            source: "images/crimson-mark.svg"
            sourceSize.width: Math.ceil(width * 2)
            sourceSize.height: Math.ceil(height * 2)
            Accessible.name: "Crimson Glass"
            Accessible.role: Accessible.Graphic
        }

        Text {
            id: title
            anchors.horizontalCenter: parent.horizontalCenter
            y: mark.y + mark.height + 25 * root.unitScale
            text: "CRIMSON GLASS"
            color: "#f4eff2"
            font.family: "Noto Sans"
            font.pixelSize: 20 * root.unitScale
            font.weight: Font.Medium
            font.letterSpacing: 4 * root.unitScale
            renderType: Text.NativeRendering
            Accessible.name: text
            Accessible.role: Accessible.StaticText
        }

        Rectangle {
            id: progressTrack
            anchors.horizontalCenter: parent.horizontalCenter
            y: title.y + title.height + 32 * root.unitScale
            width: 168 * root.unitScale
            height: 3 * root.unitScale
            radius: height / 2
            color: "#343039"

            Rectangle {
                width: parent.width * root.progress
                height: parent.height
                radius: height / 2
                color: "#e84156"
                Behavior on width {
                    NumberAnimation { duration: 260; easing.type: Easing.InOutCubic }
                }
            }
        }

        Text {
            id: status
            anchors.horizontalCenter: parent.horizontalCenter
            y: progressTrack.y + progressTrack.height + 18 * root.unitScale
            text: root.finished ? "Welcome back" : "Preparing your workspace"
            color: "#aaa4b0"
            font.family: "Noto Sans"
            font.pixelSize: 12 * root.unitScale
            font.letterSpacing: 0.5 * root.unitScale
            renderType: Text.NativeRendering
            Accessible.name: text
            Accessible.role: Accessible.StaticText

            SequentialAnimation on opacity {
                running: !root.finished
                loops: Animation.Infinite
                NumberAnimation { to: 0.60; duration: 1100; easing.type: Easing.InOutSine }
                NumberAnimation { to: 1; duration: 1100; easing.type: Easing.InOutSine }
                onStopped: status.opacity = 1
            }
        }

        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 40 * root.unitScale
            spacing: 8 * root.unitScale

            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                width: 4 * root.unitScale
                height: width
                radius: width / 2
                color: "#e84156"
            }

            Text {
                text: "KDE PLASMA"
                color: "#8e8793"
                font.family: "Noto Sans"
                font.pixelSize: 10 * root.unitScale
                font.letterSpacing: 2 * root.unitScale
                renderType: Text.NativeRendering
            }
        }
    }

    NumberAnimation {
        id: appear
        target: entrance
        property: "opacity"
        from: 0
        to: 1
        duration: 550
        easing.type: Easing.OutCubic
    }
}
