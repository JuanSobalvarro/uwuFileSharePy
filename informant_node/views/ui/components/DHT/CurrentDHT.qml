import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

ColumnLayout {
    id: column
    Layout.fillHeight: true
    Layout.fillWidth: true
    spacing: 10

    Text {
        text: "Current DHT"
        font.pixelSize: 20
        color: ThemeManager.getColor("text")
        anchors.horizontalCenter: parent.horizontalCenter
    }

    ListView {
        id: dhtList
        Layout.fillWidth: true
        Layout.fillHeight: true
        model: dhtModel

        delegate: RowLayout {
            spacing: 10

            Text {
                text: "File: " + fileName
                color: ThemeManager.getColor("text")
            }

            Text {
                text: "Host: " + host
                color: ThemeManager.getColor("text")
            }

            Text {
                text: "Port: " + port
                color: ThemeManager.getColor("text")
            }
        }
    }
}