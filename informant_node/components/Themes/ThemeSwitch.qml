/*
 * This file has the theme switcher for the Informant Node application.
 */
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import "."

Rectangle {
    id: themeSwitch
    width: 200
    height: 50
    color: "lightgray"
    border.color: "black"
    border.width: 1
    radius: 5

    RowLayout {
        anchors.fill: parent
        spacing: 10

        Button {
            text: "Light Theme"
            onClicked: {
                ThemeManager.setLight()
            }
        }

        Button {
            text: "Dark Theme"
            onClicked: {
                ThemeManager.setDark()
            }
        }
    }
}
