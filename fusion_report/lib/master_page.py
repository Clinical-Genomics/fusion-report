"""Module for MasterPage"""
class MasterPage:
    """Class defining main MasterPage. Variables are inherited for all created Pages (class Page)"""
    def __init__(self, title, partial_template):
        self.__title = title
        self.__filename = title.replace('--', '_') + ".html"
        self.__dynamic_partial = 'partials/' + partial_template + ".html"

    def get_title(self):
        """ Method returning title of the page."""
        return self.__title

    def get_filename(self):
        """ Method returning name of the page."""
        return self.__filename

    def get_content(self):
        """Helper method returning all variables. Used for Jinja templating"""
        return {
            'title': self.__title,
            'filename': self.__filename,
            'dynamic_partial': self.__dynamic_partial
        }
