from uwuFileShare.shared.viewmodels.viewmodel_factory import ViewModelFactoryBase

from uwuFileShare.informant_node.models.informant_node import InformantNode, DHT
from uwuFileShare.informant_node.viewmodels import InformantViewModel, DHTViewModel


class ViewModelFactory(ViewModelFactoryBase):
    """
    ViewModelFactory is responsible for creating view model instances based on the provided name and add it to the
    QML context.
    """

    class Models:
        DHT = "DHTViewModel"
        Informant = "InformantViewModel"

    def __init__(self, node: InformantNode, context):
        super().__init__(node, context)

    def get_functions(self):
        return {
            self.Models.Informant: self.__create_informant_view_model,
            self.Models.DHT: self.__create_dht_view_model
        }

    def __create_dht_view_model(self):
        """
        Create a DHT view model instance and bind it to the context.
        :return:
        """
        dht_view_model = DHTViewModel(self.node.dht)
        return dht_view_model

    def __create_informant_view_model(self):
        """
        Create an Informant view model instance and bind it to the context.
        :return:
        """
        informant_view_model = InformantViewModel(self.node)
        return informant_view_model
