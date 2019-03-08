"""Module for Page"""
from .master_page import MasterPage

class Page(MasterPage):
    """This class is used to define a custom Page in a report, inherits some defaults from Master"""
    def __init__(self, title, page_variables, partial_template):
        self.__page_variables = page_variables
        self.__sections = {}
        super().__init__(title, partial_template)

    def add_section(self, section):
        """
        Method for adding a new section if it doesn't exist.

        Args:
            section (Section)
        """
        if section.section_id not in self.__sections.keys():
            self.__sections[section.section_id] = section

    def get_section(self, section_id):
        """
        Method for returning section if it exists.

        Args:
            section_id (str): Defined by user, not generated in any way
        """
        return {} if self.__sections[section_id] is None else self.__sections[section_id]

    def get_content(self):
        """Helper method returning all variables. Used for Jinja templating."""
        master_content = super().get_content()
        page_content = {
            'page_variables': self.__page_variables,
            'sections': self.__sections
        }
        return {**master_content, **page_content}
