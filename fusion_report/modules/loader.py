"""Module loader"""
from typing import Any, Dict

from fusion_report.common.exceptions.module import ModuleException
from fusion_report.common.fusion_manager import FusionManager


class ModuleLoader:
    """In-house loader for custom modules."""

    def __init__(self, manager=None, params=None) -> None:
        self.manager = manager
        self.params = params

    def exec(self, name: str) -> Dict[str, Any]:
        """Executes module logic.

        Returns:
            Module result variables
        Raises:
            ModuleException
        """
        try:
            variables = self.__build_factory(name, self.manager, self.params).load()
            variables['partial'] = f'{name.replace(".", "/")}/partial.html'
            return variables
        except AttributeError as ex:
            raise ModuleException(ex)

    @classmethod
    def __build_factory(cls, name: str, manager: FusionManager, params=None):
        """Helper factory builder. Loads the correct module.

        Returns:
            an instance of CustomModule
        """
        module_name: str = f'fusion_report.modules.{name}.{name.split(".")[-1]}'
        module = __import__(module_name, fromlist=['CustomModule'])
        klass = getattr(module, 'CustomModule')
        return klass(manager, params)
