from PySide6.QtQml import QQmlContext


class ViewModelFactoryBase:
    """
    ViewModelFactory is responsible for creating view model instances based on the provided name and add it to the
    QML context.
    """
    class Models:
        """
        Models class to hold the names of the models. You should override this class in your own
        """
        pass

    def __init__(self, node, context: QQmlContext):
        self.node = node
        self.context = context

    def get_functions(self):
        """
        Return the functions dictionary. You should override this method in your own, just an example
        :return:
        """
        return {}

    def load_view_models(self):
        """
        Load the view models into the QML context.
        """
        for name in self.get_functions().keys():
            viewmodel = self.__get_viewmodel(name, self.context)
            self.context.setContextProperty(name, viewmodel)
            print(f"[+] Loaded ViewModel: {name}")

    def __get_viewmodel(self, name: str, context):
        """
        Return an instance of the corresponding viewmodel class based on the name provided.
        :param name:
        :param context:
        :return:
        """

        if name is None:
            raise ValueError("ViewModel name cannot be None")

        return self.get_functions()[name]()
