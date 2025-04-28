import os
import sys
import importlib
from typing import Callable

from PySide6.QtCore import QCoreApplication, QUrl, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from .resource_compiler import build_resources
from ..viewmodels.viewmodel_factory import ViewModelFactoryBase


class GUI:
    def __init__(
        self,
        app_name: str = "QtApp",
        node=None,
        import_path_dirs: list[str] = None,
        entry_file_path: str = None,
        view_models_dir: str = None,
        view_model_factory: ViewModelFactoryBase = None,
        resource_kwargs: dict = None,
    ):
        self.import_path_dirs = import_path_dirs or []
        self.entry_file_path = entry_file_path
        self.view_models_dir = view_models_dir
        self.node = node
        self.app = QGuiApplication()
        self.app.setApplicationName(app_name)

        self.engine = QQmlApplicationEngine()
        self.view_model_factory = None

        # Compile QRC Resources
        resource_kwargs = resource_kwargs or {}
        resource_module_path = build_resources(**resource_kwargs)
        if resource_module_path:
            print("Importing module form path:", resource_module_path)
            importlib.import_module(resource_module_path)

        # Instantiate the ViewModel factory if provided
        if view_model_factory:
            self.view_model_factory = view_model_factory(node=self.node, context=self.engine.rootContext())

        self.__generate_qmldir_files()
        self.__add_import_paths()
        if self.view_model_factory:
            self.view_model_factory.load_view_models()
        self.__load_entry_file()

        self.engine.objectCreated.connect(self.handle_object_created, Qt.ConnectionType.QueuedConnection)

    def __generate_qmldir_files(self):
        for import_dir in self.import_path_dirs:
            if not os.path.isdir(import_dir):
                print(f"[!] Import path does not exist: {import_dir}")
                continue

            for module_dir in os.listdir(import_dir):
                module_path = os.path.join(import_dir, module_dir)
                if not os.path.isdir(module_path):
                    continue

                qmldir_path = os.path.join(module_path, "qmldir")
                qml_files = [f for f in os.listdir(module_path) if f.endswith(".qml")]

                with open(qmldir_path, "w") as qmldir_file:
                    qmldir_file.write(f"module {module_dir}\n")
                    for qml_file in qml_files:
                        component_name = os.path.splitext(qml_file)[0]
                        prefix = ""

                        with open(os.path.join(module_path, qml_file), "r") as f:
                            if f.readline().strip().startswith("pragma Singleton"):
                                prefix = "singleton "

                        qmldir_file.write(f"{prefix}{component_name} {qml_file}\n")
                print(f"[+] Created qmldir: {qmldir_path}")

    def __add_import_paths(self):
        for import_dir in self.import_path_dirs:
            if os.path.isdir(import_dir) and os.listdir(import_dir):
                self.engine.addImportPath(import_dir)
                print(f"[+] Added import path: {import_dir}")

    def __load_entry_file(self):
        if self.entry_file_path:
            self.engine.load(QUrl.fromLocalFile(self.entry_file_path))
            print(f"[+] Loaded entry file: {self.entry_file_path}")
        else:
            print("[!] No entry file path provided.")

    def handle_object_created(self, obj, obj_url):
        if obj is None and QUrl.fromLocalFile(self.entry_file_path) == obj_url:
            print(f"[!] Failed to load QML file: {self.entry_file_path}")
            QCoreApplication.exit(-1)
