"""Report class"""
from typing import Any, Dict, List, Optional

from fusion_report.common.exceptions.report import ReportException
from fusion_report.common.page import Page
from fusion_report.common.template import Template


class Report(Template):
    """Report is the base container containing all types of pages.

    Attributes:
        pages: List of pages
    """

    def __init__(self, config_path: str, output_dir: str) -> None:
        self.pages: List[Page] = []
        super().__init__(config_path, output_dir)

    def create_page(
        self,
        title: str,
        view: str = "index",
        filename: str = None,
        page_variables: Dict[str, Any] = None,
    ) -> Page:
        """Creates and adds page in the list.

        Return:
            page: Page object

        Raises:
            ReportException
        """
        if page_variables is None:
            page_variables = {}

        page = Page(title, view, filename, page_variables)
        if self.index_by(filename) != -1:
            raise ReportException(f"Page {page.filename} already exists!")

        self.pages.append(page)
        return page

    def get_page(self, filename: str) -> Page:
        """Search page by its file name.

        Returns:
            page

        Raises:
            ReportException
        """
        index = self.index_by(filename)
        if index == -1:
            raise ReportException(f"Page {filename} not found")

        return self.pages[index]

    def render(self, page: Page, extra_variables: Optional[Dict[str, Any]] = None):
        """Method for rendering page using templating engine."""
        template_variables: Dict[str, Any] = page.get_content()

        # load modules
        template_variables["modules"] = page.modules

        # generate menu (html_id, menu item): List[Tuple[str, str]]
        template_variables["menu"] = []
        for _, module in template_variables["modules"].items():
            for item in module["menu"]:
                template_variables["menu"].append((self.get_id(item), item))

        if extra_variables:
            template_variables = {**template_variables, **extra_variables}

        super().render(page, template_variables)

    def index_by(self, value: Optional[str]) -> int:
        """Find page based on its filename.

        Return:
            >= 0: page exists
            -1: page doesn't exist
        """
        if value:
            for index, page in enumerate(self.pages):
                if page.filename == value:
                    return index

        return -1
