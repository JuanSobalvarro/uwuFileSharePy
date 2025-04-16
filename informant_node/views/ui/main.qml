import QtQuick
import QtQuick.Layouts
import Themes
import DHT

Window {
    id: root
    width: 1000
    height: 500
    visible: true
    title: "Informant Node"
    color: "#383838"

    property var separator_width: 5

    RowLayout {
        id: main
        anchors.fill: parent
        spacing: 0

        Rectangle {
            id: leftColumn
            color: ThemeManager.getColor("background")
            Layout.fillHeight: true
            Layout.fillWidth: true
        }

        // Separator
        Rectangle {
            id: separator1
            color: "yellow"
            Layout.fillHeight: true
            Layout.preferredWidth: separator_width
        }

        Rectangle {
            id: connected_nodes
            color: "green"
            Layout.fillHeight: true
            Layout.fillWidth: true
        }

        // Separator
        Rectangle {
            id: separator2
            color: "yellow"
            Layout.fillHeight: true
            Layout.preferredWidth: separator_width
        }

        Rectangle {
            id: known_nodes
            color: "blue"
            Layout.fillHeight: true
            Layout.fillWidth: true
        }
    }

    // Theme switch from themes add it at the right bottom corner
    ThemeSwitch {
        id: themeSwitch
        anchors.right: parent.right
        anchors.bottom: parent.bottom
    }

    Component.onCompleted: {
        console.log("Main QML component loaded")
        console.log("ThemeManager loaded?", ThemeManager !== undefined)
        console.log("Current theme is: ", ThemeManager.currentThemeName)
        // ThemeManager.setLight()  // Also triggers the console.log inside ThemeManager
    }
}
