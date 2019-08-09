from fusion_report.common.logger import Logger

class ModuleLoader:

    def __init__(self, manager=None):
        self.manager = manager

    def exec(self, name: str):
        try:
            variables = self.__build_factory(name, self.manager).load()
            variables['partial'] = f'{name}/partial.html'
            return variables
        except AttributeError as ex:
            Logger().get_logger().exception(ex)

    def __build_factory(self, name: str, manager):
        module_name: str = f'fusion_report.modules.{name}.{name}'
        module = __import__(module_name, fromlist=['CustomModule'])
        klass = getattr(module, 'CustomModule')
        return klass(manager)
