"""Module for MasterPage"""
class MasterPage:
    """Class defining main MasterPage. Variables are inherited for all created Pages (class Page)"""
    def __init__(self, title, partial_template):
        self.__title = title
        self.__filename = title.replace('--', '_') + ".html"
        self.__dynamic_partial = 'partials/' + partial_template + ".html"

    def get_title(self):
        return self.__title

    def get_filename(self):
        return self.__filename

    def get_content(self, page_content):
        """Helper method returning all variables. Used for Jinja templating"""
        master_content = {
            'title': self.__title,
            'filename': self.__filename,
            'dynamic_partial': self.__dynamic_partial
        }
        
        return {**master_content, **page_content}
