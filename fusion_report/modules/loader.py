from fusion_report.common.fusion_manager import FusionManager
from fusion_report.common.logger import Logger


class ModuleLoader:

    def __init__(self, manager=None, params=None):
        self.manager = manager
        self.params = params

    def exec(self, name: str):
        try:
            variables = self.__build_factory(name, self.manager, self.params).load()
            variables['partial'] = f'{name}/partial.html'
            return variables
        except AttributeError as ex:
            Logger().get_logger().exception(ex)

    @classmethod
    def __build_factory(cls, name: str, manager: FusionManager, params=None):
        module_name: str = f'fusion_report.modules.{name}.{name}'
        module = __import__(module_name, fromlist=['CustomModule'])
        klass = getattr(module, 'CustomModule')
        return klass(manager, params)
