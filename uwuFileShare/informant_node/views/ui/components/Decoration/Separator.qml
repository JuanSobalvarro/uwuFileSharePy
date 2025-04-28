import QtQuick
import QtQuick.Layouts

Rectangle {
    id: separator
    color: separatorColor
    radius: 2

    // Default size — can be overridden
    width: defaultWidth
    height: defaultHeight

    // Properties to allow customization
    property color separatorColor: "#999999"
    property int defaultWidth: 1
    property int defaultHeight: 1

    // Use Layout properties for flexibility in layouts
    Layout.preferredWidth: defaultWidth
    Layout.preferredHeight: defaultHeight
    Layout.fillWidth: fillWidth
    Layout.fillHeight: fillHeight

    // Boolean toggles to fill space
    property bool fillWidth: false
    property bool fillHeight: false
}
