"""Module for Page"""
from typing import Any, Dict

from fusion_report.common.base_page import BasePage


class Page(BasePage):
    """This class is used to define a custom Page in a report, inherits some defaults from Master"""
    def __init__(self, title: str, filename: str, view: str, page_variables: Dict[str, Any]):
        super().__init__(title, filename, view)
        self.__page_variables = page_variables

    def get_content(self):
        """Helper method returning all variables. Used for Jinja templating."""
        master_content = super().get_content()
        page_content = {
            'page_variables': self.__page_variables,
            'sections': []
        }
        return {**master_content, **page_content}
