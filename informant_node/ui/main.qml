import QtQuick
import QtQuick.Layouts
import Themes

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

        ColumnLayout {
            id: left_column
            Layout.fillHeight: true
            Layout.fillWidth: true
            spacing: 0

            Rectangle {
                id: left_column_background
                color: ThemeManager.currentTheme.background
                Layout.fillHeight: true
                Layout.fillWidth: true

                Text {
                    id: left_column_title
                    text: "Current DHT"
                    color: "white"
                    font.pixelSize: 20
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
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

    // Theme switch from themes
    ThemeSwitch {
        id: themeSwitch
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 10
    }

    Component.onCompleted: {
        console.log("Main QML component loaded")
        console.log("ThemeManager loaded?", ThemeManager !== undefined)
        console.log("Current theme is: ", ThemeManager.currentTheme)
        // ThemeManager.setLight()  // Also triggers the console.log inside ThemeManager
    }
}
