pragma Singleton
import QtQuick

QtObject {
    id: themes

    property var themes_options : [
        {
            name: "light",
            description: "Light theme with bright colors"
        },
        {
            name: "dark",
            description: "Dark theme with muted colors"
        }
    ]

    property var background: ({
        "light": "#ffffff",
        "dark": "#1e1e1e"
    })

    property var background_sel: ({
        "light": "#aaaaaa",
        "dark": "#444444"
    })

    property var text: {
        "light": "#1e1e1e",
        "dark": "#f2f2f2"
    }

    property var primary: {
        "light": "#cc77ee",
        "dark": "#aa55cc"
    }

    property var accent: {
        "light": "#e0e0e0",
        "dark": "#2d2d30"
    }

    property var error: {
        "light": "#ff0000",
        "dark": "#ff0000"
    }

    property var popup: {
        "light": "#ffffff",
        "dark": "#1e1e1e"
    }

    property var popup_border: {
        "light": "#333333",
        "dark": "#aaaaaa"
    }
}
