import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 600
    height: 400
    title: "P2P File Sharing"

    Column {
        spacing: 10
        padding: 10

        TextField {
            id: fileInput
            placeholderText: "Enter file name to share"
        }

        Button {
            text: "Add File to Share"
            onClicked: {
                peerNode.addFileToShare(fileInput.text)
                fileInput.text = ""
            }
        }

        Label { text: "Shared Files:" }
        ListView {
            id: sharedFilesList
            width: parent.width
            height: 100
            model: peerNode.sharedFiles
            delegate: Text { text: modelData }
        }

        Button {
            text: "Refresh DHT"
            onClicked: peerNode.refreshDHT()
        }

        Label { text: "Files in Network:" }
        ListView {
            id: dhtList
            width: parent.width
            height: 100
            model: peerNode.dhtFiles
            delegate: Text { text: modelData }
        }

        Button {
            text: "Download Selected File"
            onClicked: peerNode.downloadFile(dhtList.currentIndex)
        }
    }
}
