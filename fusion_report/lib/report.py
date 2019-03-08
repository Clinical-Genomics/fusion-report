"""Module for Report"""
from .report_config import ReportConfig
from .template import Template

class Report(Template):
    """Class containing core functionality for generating report"""
    def __init__(self, config, output_dir):
        self.pages = []
        config = ReportConfig(config).get_variables()
        super().__init__(config, output_dir)

    def add_page(self, page):
        """
        Helper function for adding a page
        Args:
            page (class Page)
        """
        if page.get_filename() in self.pages:
            print('Page ' + page.filename + ' already exists, skipping ...')
        else:
            # using filenames as identifiers
            self.pages.append(page.get_filename())
            # after adding immediately generate fusion page
            self.render(page)

    def render(self, page, template_variables=''):
        """Helper method rendering page using Jinja template engine."""
        template_variables = page.get_content()
        template_variables['menu'] = [
            (key, page.get_section(key).title) for key in template_variables['sections'].keys()
        ]
        super().render(page, template_variables)
