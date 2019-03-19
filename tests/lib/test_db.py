import pytest
import sqlite3
from fusion_report.lib.db import Db

@pytest.fixture()
def get_empty_instance():
    test_db = Db('tests/test_data')
    test_db.connect('empty')
    return test_db

def test_init():
    with pytest.raises(SystemExit):
        Db()

def test_connect():
    with pytest.raises(SystemExit):
        Db('tests/test_data/').connect('unknown')

def test_get_db_names(get_empty_instance):
    assert get_empty_instance.get_db_names() == ['empty']

def test_select(get_empty_instance):
    with pytest.raises(SystemExit):
        get_empty_instance.select('SELECT * FROM NONE')

def test_scan_folder(get_empty_instance):
    with pytest.raises(SystemExit):
        Db('/path/with/no/existance')
    assert get_empty_instance.get_db_names() == ['empty']
