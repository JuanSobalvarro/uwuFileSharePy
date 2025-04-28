import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Themes
import Decoration

Rectangle {
    id: main
    color: ThemeManager.getColor("background")

    property var column_width: width / 3 - 20

    ColumnLayout {
        anchors.fill: parent
        spacing: 16

        Label {
            text: "Current DHT"
            font.pixelSize: 24
            font.bold: true
            color: ThemeManager.getColor("text")
            horizontalAlignment: Text.AlignHCenter
            Layout.alignment: Qt.AlignHCenter
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: ThemeManager.getColor("background_sel")

            ColumnLayout {
                anchors.fill: parent
                Layout.alignment: Qt.AlignHCenter
                spacing: 8

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "File Name"
                        font.bold: true
                        Layout.preferredWidth: column_width
                        color: ThemeManager.getColor("text")
                    }
                    Label {
                        text: "Host"
                        font.bold: true
                        Layout.preferredWidth: column_width
                        color: ThemeManager.getColor("text")
                    }
                    Label { text: "Port"
                        font.bold: true
                        Layout.preferredWidth: column_width
                        color: ThemeManager.getColor("text")
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 1
                    color: ThemeManager.getColor("popup_border")
                }

                // Data List
                ListView {
                    id: dhtList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    model: DHTViewModel
                    clip: true
                    spacing: 4

                    delegate: RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        property bool even: index % 2 === 0
                        property color bgColor: even
                            ? ThemeManager.getColor("selection_1")
                            : ThemeManager.getColor("selection_2")

                        // File Name column
                        Rectangle {
                            height: 28
                            Layout.fillWidth: true
                            Layout.preferredWidth: column_width
                            radius: 4
                            color: bgColor

                            Label {
                                anchors.centerIn: parent
                                text: fileName
                                color: ThemeManager.getColor("text")
                            }
                        }

                        // Host column
                        Rectangle {
                            height: 28
                            Layout.fillWidth: true
                            Layout.preferredWidth: column_width
                            radius: 4
                            color: bgColor

                            Label {
                                anchors.centerIn: parent
                                text: host
                                color: ThemeManager.getColor("text")
                            }
                        }

                        // Port column
                        Rectangle {
                            height: 28
                            Layout.fillWidth: true
                            Layout.preferredWidth: column_width
                            radius: 4
                            color: bgColor

                            Label {
                                anchors.centerIn: parent
                                text: port
                                color: ThemeManager.getColor("text")
                            }
                        }
                    }
                }
            }
        }
    }
}
