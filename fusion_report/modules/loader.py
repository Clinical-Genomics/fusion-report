from fusion_report.common.logger import Logger

class ModuleLoader:

    def exec(self, name: str):
        try:
            variables = self.__build_factory(name).load()
            variables['partial'] = f'{name}/partial.html'
            return variables
        except AttributeError as ex:
            Logger().get_logger().exception(ex)

    def __build_factory(self, name):
        module_name: str = f'fusion_report.modules.{name}.{name}'
        module = __import__(module_name, fromlist=['CustomModule'])
        klass = getattr(module, 'CustomModule')
        return klass()
