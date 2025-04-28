# Project Architecture
This project follows the MVVM (Model-View-ViewModel) architecture pattern, which separates the user interface (UI) from the business logic and data. This separation allows for better organization, maintainability, and testability of the code.

## Components
- **Model**: Represents the data and business logic of the application. It is responsible for managing the data, including fetching, storing, and processing it. In this project, the model is represented by the `model` package.
- **View**: Represents the UI components of the application. It is responsible for displaying the data to the user and handling user interactions. In this project, the view is represented by the `view` package.
- **ViewModel**: Acts as a bridge between the Model and the View. It retrieves data from the Model and prepares it for display in the View. It also handles user interactions and updates the Model accordingly. In this project, the ViewModel is represented by the `viewmodel` package.

## Technologies
We use the following technologies in this project:
- **Python**: The programming language used for the project.
- **PySide6**: The framework used for building the GUI. It provides a set of Python bindings for the Qt libraries, allowing us to create cross-platform applications with a native look and feel.
- **QtQuick**: A UI toolkit for creating fluid and dynamic user interfaces. It is used in conjunction with PySide6 to create the application's UI.

## UWU Protocol
This project uses TCP/IP for communication and uses a custom application layer protocol called uwu-protocol. 
The protocol is designed to be simple and easy, allowing for easy communication between nodes. 

### Protocol Structure
- **Message**: The basic unit of communication in the protocol. A message is formatted in JSON and data like this:
```json
{
    "type": "message_type[request, response, event, etc]",
    "action": "action_selection[get_dht, register, error, success, etc]",
    "data": {
        "key": "value" 
    }
}
```
