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
        width: parent.width
        anchors.fill: parent
        spacing: 16

        Label {
            text: "Nodes Connected"
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

                Label {
                    text: "Here you can visualize the nodes connected to your client. The nodes are represented by their IP address and port number. You can also see the number of files shared by each node."
                    font.pixelSize: 12
                    color: ThemeManager.getColor("text")
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: parent.width * 0.9
                    wrapMode: Text.WordWrap
                }

                Separator {
                    Layout.fillWidth: true
                    color: ThemeManager.getColor("text")
                }

                ListView {
                    id: connected_nodes_list
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    spacing: 10
                    clip: true
                    model: InformantViewModel.connectedNodesModel

                    delegate: Item {
                        width: parent.width
                        height: 50

                        Rectangle {
                            width: parent.width
                            height: 50
                            color: ThemeManager.getColor("background_sel")
                            border.color: ThemeManager.getColor("text")
                            border.width: 1

                            RowLayout {
                                anchors.fill: parent
                                spacing: 10

                                Label {
                                    text: model.host + ":" + model.port  // Corrected to use model's role names
                                    font.pixelSize: 16
                                    color: ThemeManager.getColor("text")
                                    horizontalAlignment: Text.AlignHCenter
                                    Layout.alignment: Qt.AlignHCenter
                                }

                                Label {
                                    text: model.files + " files"
                                    font.pixelSize: 16
                                    color: ThemeManager.getColor("text")
                                    horizontalAlignment: Text.AlignHCenter
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: {
        console.log("---------------------Connected Nodes View Loaded: ", InformantViewModel, " nodes connected.");
    }
}
