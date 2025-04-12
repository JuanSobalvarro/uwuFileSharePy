pragma Singleton
import QtQuick
import "."

QtObject {
    property QtObject currentTheme: LightTheme

    function setLight() {
        currentTheme = LightTheme
        console.log("Light theme set")
    }

    function setDark() {
        currentTheme = DarkTheme
        console.log("Dark theme set")
    }
}

