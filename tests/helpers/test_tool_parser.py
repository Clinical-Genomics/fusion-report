import pytest
from fusion_report.helpers.tool_parser import ToolParser

def test_empty_fusions():
    """ Init ToolParser should have 0 fusions """
    assert not bool(ToolParser().get_fusions())

def test_empty_tools():
    """ Init ToolParser should have 0 fusions """
    assert ToolParser().get_tools() == []
