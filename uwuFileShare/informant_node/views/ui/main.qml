import QtQuick
import QtQuick.Layouts
import Themes
import DHT
import Nodes
import Decoration

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

        CurrentDHT {
            id: current_dht
            Layout.fillHeight: true
            Layout.fillWidth: true
        }

        // Separator
        Separator {
            id: separator1
            separatorColor: "yellow"
            defaultWidth: separator_width
            fillHeight: true
        }

        ConnectedNodes {
            id: connected_nodes
            Layout.fillHeight: true
            Layout.fillWidth: true
        }

        Separator {
            id: separator2
            separatorColor: "yellow"
            defaultWidth: separator_width
            fillHeight: true
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
