"""Page class"""
from typing import Any, Dict

from fusion_report.common.base_page import BasePage


class Page(BasePage):
    """Page implementation. The report is build from a list of pages.

    Attributes:
        __page_variables: extra variables to be displayed on the page
    """
    def __init__(self, title: str, view: str,
                 filename: str = None, page_variables: Dict[str, Any] = None) -> None:
        self.__page_variables = {} if not page_variables else page_variables
        super().__init__(title, view, filename)

    def get_content(self) -> Dict[str, Any]:
        """Helper serialization method for templating engine."""
        master_content: Dict[str, Any] = super().get_content()
        page_variables = {**master_content, **self.__page_variables}

        return page_variables
