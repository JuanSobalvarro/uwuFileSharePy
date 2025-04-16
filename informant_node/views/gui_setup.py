import os
import importlib

from PySide6.QtCore import QCoreApplication, QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from resource_compiler import build_resources


class GUI:
    def __init__(self, informant_node, import_path_dirs: list[str] = None, entry_file_path: str = None, view_models_dir: str = None):
        self.import_path_dirs = import_path_dirs or []
        self.entry_file_path = entry_file_path
        self.view_models_dir = view_models_dir
        self.node = informant_node
        self.app = QGuiApplication()
        self.app.setApplicationName("Informant Node")

        self.engine = QQmlApplicationEngine()

        # Compile resources
        resource_module_path = build_resources()
        importlib.import_module(resource_module_path)

        # Generate qmldir files, add import paths, and load the entry file
        self.__generate_qmldir_files()
        self.__add_import_paths()
        self.__load_viewmodels()
        self.__load_entry_file()

        # Connect the fail-safe handler for QML loading
        self.engine.objectCreated.connect(self.handle_object_created, Qt.ConnectionType.QueuedConnection)

    def __generate_qmldir_files(self):
        """
        Generate qmldir files for the import paths. Import paths are directories which inside contains a module
        (defined in qmldir file).
        """
        for import_dir in self.import_path_dirs:
            # Check if the directory exists
            if not os.path.isdir(import_dir):
                print(f"[!] Import path does not exist: {import_dir}")
                continue

            # Iterate over all directories inside the import path (remember each directory is a module)
            for module_dir in os.listdir(import_dir):
                module_path = os.path.join(import_dir, module_dir)

                if not os.path.isdir(module_path):
                    print(f"[!] Not a directory: {module_path}")
                    continue

                qmldir_path = os.path.join(module_path, "qmldir")

                # Check if the qmldir file already exists
                # if os.path.exists(qmldir_path):
                #     print(f"[!] qmldir file already exists: {qmldir_path}. Skipping automatic generation.")
                #     continue

                # Now iterate over all QML files in the module directory and save it to add it to the qmldir file
                qml_files = [f for f in os.listdir(module_path) if f.endswith(".qml")]

                # Create the qmldir file
                with open(qmldir_path, "w") as qmldir_file:
                    qmldir_file.write(f"module {module_dir}\n")
                    # Write all QML files to the qmldir file as: ComponentName ComponentName.qml
                    for qml_file in qml_files:
                        component_name = os.path.splitext(qml_file)[0]
                        start = ""

                        # if component starts with pragma Singleton, we should add singleton to the qmldir file
                        with open(os.path.join(module_path, qml_file), "r") as qml_file_obj:
                            first_line = qml_file_obj.readline().strip()
                            if first_line.startswith("pragma Singleton"):
                                start = "singleton "

                        qmldir_str = f"{start}{component_name} {qml_file}\n"
                        qmldir_file.write(qmldir_str)

                    print(f"[+] Created qmldir file: {qmldir_path}")

    def __add_import_paths(self):
        """
        Add import paths for QML files.
        """
        for import_dir in self.import_path_dirs:
            # If the dir exists and there is at least one QML file in it add it
            if os.path.isdir(import_dir) and len(os.listdir(import_dir)) > 0:
                self.engine.addImportPath(import_dir)
                print(f"[+] Added import path: {import_dir}")

    def __load_viewmodels(self):
        """
        Automatically imports and registers viewmodels in a directory.
        Assumes each ViewModel is in '\viewmodels' and named `xxx_vm.py` containing a class named `XxxViewModel`.
        """
        context = self.engine.rootContext()

        for file in os.listdir(self.view_models_dir):
            if not file.endswith("_vm.py"):
                continue

            module_name = file[:-3]  # remove .py
            class_name = ''.join(
                [part.capitalize() for part in module_name.replace("_vm", "").split("_")]) + "ViewModel"

            try:
                module = importlib.import_module(f"views.viewmodels.{module_name}")
                ViewModelClass = getattr(module, class_name)
                instance = ViewModelClass()
                context.setContextProperty(module_name.replace("_vm", "VM"), instance)
                print(f"[+] Auto-registered ViewModel: {class_name}")
            except (ImportError, AttributeError) as e:
                print(f"[!] Failed to load {file}: {e}")


    def __load_entry_file(self):
        """
        Load the entry QML file.
        """
        if self.entry_file_path:
            self.engine.load(QUrl.fromLocalFile(self.entry_file_path))
            print(f"[+] Loaded entry file: {self.entry_file_path}")
        else:
            print("[!] No entry file path provided.")

    def handle_object_created(self, obj, obj_url):
        """
        Handles the object creation signal from the engine.
        If loading the QML file fails, it exits the application.
        """
        if obj is None and QUrl.fromLocalFile(self.entry_file_path) == obj_url:
            print(f"[!] Failed to load QML file: {self.entry_file_path}")
            QCoreApplication.exit(-1)  # Exit with error code

