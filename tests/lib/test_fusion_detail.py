import pytest
from fusion_report.lib.fusion_detail import FusionDetail

@pytest.fixture
def fusion_detail():
    return FusionDetail()

def test_init(fusion_detail):
    assert fusion_detail.score == 0.0
    assert fusion_detail.tools == dict()
    assert len(fusion_detail.dbs) == 0

def test_add_tool(fusion_detail):
    fusion_detail.add_tool('fusioncatcher', {})
    fusion_detail.add_tool('fusioncatcher', {})
    assert 'fusioncatcher' in fusion_detail.tools
    assert len(fusion_detail.tools) == 1

def test_add_db(fusion_detail):
    fusion_detail.add_db('fusiongdb')
    fusion_detail.add_db('fusiongdb')
    assert 'fusiongdb' in fusion_detail.dbs
    assert len(fusion_detail.dbs) == 1
