import pytest
from fusion_report.lib.tool_parser import ToolParser
from fusion_report.lib.fusion_detail import FusionDetail

FUSIONCATCHER_FOUND_FUSIONS = 17
FUSIONCATCHER_AND_ERICSCRIPT = 17
ERICSCRIPT_FOUND_FUSIONS = 12
PIZZLY_FOUND_FUSIONS = 8
SQUID_FOUND_FUSIONS = 7
STARFUSION_FOUND_FUSIONS = 10

@pytest.fixture
def tool_parser():
    return ToolParser()

def get_first_fusion_line(file):
    test_file = open(f'tests/test_data/{file}', 'r', encoding='utf-8')
    test_file.readline() # skip header
    first_line = test_file.readline().strip().split('\t')
    test_file.close()
    return first_line

def test_init(tool_parser):
    assert not bool(tool_parser.get_fusions())
    assert tool_parser.get_tools() == []

@pytest.mark.parametrize("test_tool,test_file, exp_fusion_length, exp_tools", [
    ('fusioncatcher', 'tests/test_data/fusioncatcher.txt', FUSIONCATCHER_FOUND_FUSIONS, ['fusioncatcher']),
    ('ericscript', 'tests/test_data/ericscript.tsv', ERICSCRIPT_FOUND_FUSIONS, ['ericscript']),
    ('pizzly', 'tests/test_data/pizzly.tsv', PIZZLY_FOUND_FUSIONS, ['pizzly']),
    ('squid', 'tests/test_data/squid.txt', SQUID_FOUND_FUSIONS, ['squid']),
    ('starfusion', 'tests/test_data/starfusion.tsv', STARFUSION_FOUND_FUSIONS, ['starfusion'])
])
def test_parse(tool_parser, test_tool, test_file, exp_fusion_length, exp_tools):
    tool_parser.parse(test_tool, test_file)
    fusions = tool_parser.get_fusions()
    assert len(fusions) == exp_fusion_length
    assert tool_parser.get_tools() == exp_tools

def test_parse_multiple_tools(tool_parser):
    tool_parser.parse('fusioncatcher', 'tests/test_data/fusioncatcher.txt')
    tool_parser.parse('ericscript', 'tests/test_data/ericscript.tsv')
    assert len(tool_parser.get_fusions()) == FUSIONCATCHER_AND_ERICSCRIPT
    assert tool_parser.get_tools() == ['fusioncatcher', 'ericscript']
    # Verify details info for fusion FGFR3--TACC3
    fgfr3_tacc3 = tool_parser.get_fusion('FGFR3--TACC3')
    assert len(fgfr3_tacc3.tools['ericscript']) == 1
    assert len(fgfr3_tacc3.tools['fusioncatcher']) == 2

def test_parse_wrong_file(tool_parser):
    with pytest.raises(SystemExit):
        tool_parser.parse('fusioncatcher', 'tests/test_data/fail.txt')

def test_get_fusion(tool_parser):
    assert tool_parser.get_fusion('unknown') == {}
    tool_parser.parse('ericscript', 'tests/test_data/ericscript.tsv')
    print(tool_parser.get_fusion('FGFR3--TACC3'))
    assert isinstance(tool_parser.get_fusion('FGFR3--TACC3'), FusionDetail)

def test_get_fusions(tool_parser):
    assert len(tool_parser.get_fusions()) == 0

def test_ericscript():
    first_line = get_first_fusion_line('ericscript.tsv')
    fusion, _ = ToolParser.ericscript(first_line)
    assert "AKAP9--BRAF" == fusion

def test_fusioncatcher():
    first_line = get_first_fusion_line('fusioncatcher.txt')
    fusion, _ = ToolParser.fusioncatcher(first_line)
    assert "FGFR3--TACC3" == fusion

def test_pizzly():
    first_line = get_first_fusion_line('pizzly.tsv')
    fusion, _ = ToolParser.pizzly(first_line)
    assert "AKAP9--BRAF" == fusion

def test_squid():
    first_line = get_first_fusion_line('squid.txt')
    fusion, _ = ToolParser.squid(first_line)
    assert "FGFR3--TACC3" == fusion

def test_star_fusion():
    first_line = get_first_fusion_line('starfusion.tsv')
    fusion, _ = ToolParser.starfusion(first_line)
    assert "FGFR3--TACC3" == fusion
