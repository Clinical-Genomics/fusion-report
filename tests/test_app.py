"""Unit tests for App.enrich() and App.score()."""

from argparse import Namespace

import pytest

from fusion_report import app as app_module
from fusion_report.app import App
from fusion_report.common.exceptions.app import AppException
from fusion_report.common.models.fusion import Fusion
from fusion_report.common.singleton import Singleton

TOOLS = [
    "ericscript",
    "fusioncatcher",
    "starfusion",
    "ctat_lr_fusion",
    "arriba",
    "pizzly",
    "squid",
    "dragen",
    "jaffa",
]

# Each fake database knows exactly one fusion, so enrich() results show which DBs were read.
DB_FUSIONS = {
    "COSMIC": "COSMIC1--COSMIC2",
    "Mitelman": "MITELMAN1--MITELMAN2",
    "FusionGDB2": "FGDB1--FGDB2",
}


def make_fake_db(db_name):
    class FakeDB:
        def __init__(self, path):
            self.name = db_name

        def get_all_fusions(self):
            return [DB_FUSIONS[db_name]]

    return FakeDB


def make_params(db_path, no_cosmic=False, no_mitelman=False, no_fusiongdb2=False, tools=None):
    params = {tool: None for tool in TOOLS}
    params.update(tools or {})
    return Namespace(
        db_path=str(db_path),
        no_cosmic=no_cosmic,
        no_mitelman=no_mitelman,
        no_fusiongdb2=no_fusiongdb2,
        **params,
    )


@pytest.fixture
def fusion_app():
    application = App()
    for name in DB_FUSIONS.values():
        application.manager.fusions.append(Fusion(name))
    return application


@pytest.fixture
def fake_dbs(monkeypatch, tmp_path):
    """Replace the database classes with fakes and create (empty) database files."""
    monkeypatch.setattr(app_module, "CosmicDB", make_fake_db("COSMIC"))
    monkeypatch.setattr(app_module, "MitelmanDB", make_fake_db("Mitelman"))
    monkeypatch.setattr(app_module, "FusionGDB2", make_fake_db("FusionGDB2"))
    for name in DB_FUSIONS:
        (tmp_path / f"{name.lower()}.db").touch()
    return tmp_path


def enriched_dbs(application):
    return sorted(db for fusion in application.manager.fusions for db in fusion.dbs)


def test_enrich_all_dbs(fusion_app, fake_dbs):
    fusion_app.enrich(make_params(fake_dbs))
    assert enriched_dbs(fusion_app) == sorted(DB_FUSIONS)


@pytest.mark.parametrize(
    "flag, skipped",
    [
        ("no_cosmic", "COSMIC"),
        ("no_mitelman", "Mitelman"),
        ("no_fusiongdb2", "FusionGDB2"),
    ],
)
def test_enrich_flag_skips_its_own_db(fusion_app, fake_dbs, flag, skipped):
    # Remove the skipped database file to make sure it is never opened.
    (fake_dbs / f"{skipped.lower()}.db").unlink()
    fusion_app.enrich(make_params(fake_dbs, **{flag: True}))
    assert enriched_dbs(fusion_app) == sorted(set(DB_FUSIONS) - {skipped})


def test_enrich_no_cosmic_no_fusiongdb2_uses_mitelman_only(fusion_app, fake_dbs):
    (fake_dbs / "cosmic.db").unlink()
    (fake_dbs / "fusiongdb2.db").unlink()
    fusion_app.enrich(make_params(fake_dbs, no_cosmic=True, no_fusiongdb2=True))
    assert enriched_dbs(fusion_app) == ["Mitelman"]


def test_enrich_missing_db_raises_and_creates_no_file(fusion_app, tmp_path, monkeypatch):
    # Use the real database classes, but make sure no cached singleton instance is reused.
    monkeypatch.setattr(Singleton, "_instances", {})
    params = make_params(tmp_path, no_cosmic=True, no_mitelman=True)
    with pytest.raises(AppException, match="--no-fusiongdb2"):
        fusion_app.enrich(params)
    assert not (tmp_path / "fusiongdb2.db").exists()


def test_score_with_all_dbs(fusion_app):
    fusion = fusion_app.manager.fusions[0]
    fusion.add_tool("arriba", {})
    fusion.add_db("COSMIC")
    params = make_params("db", tools={"arriba": "a.tsv", "starfusion": "s.tsv"})
    fusion_app.score(params)
    # 0.5 * (1 / 2) + 0.5 * (0.5 / 1)
    assert fusion.score == 0.5
    assert fusion.score_explained == "0.5 * (1 / 2) + 0.5 * (0.5 / 1)"


def test_score_no_cosmic_no_fusiongdb2(fusion_app):
    fusion = fusion_app.manager.fusions[0]
    fusion.add_tool("arriba", {})
    fusion.add_db("Mitelman")
    params = make_params("db", no_cosmic=True, no_fusiongdb2=True, tools={"arriba": "a.tsv"})
    fusion_app.score(params)
    # 0.5 * (1 / 1) + 0.5 * (0.5 / 0.5)
    assert fusion.score == 1.0


def test_score_without_weighted_dbs(fusion_app):
    """--no-cosmic --no-mitelman leaves no weighted database: no ZeroDivisionError."""
    fusion = fusion_app.manager.fusions[0]
    fusion.add_tool("arriba", {})
    fusion.add_db("FusionGDB2")
    params = make_params("db", no_cosmic=True, no_mitelman=True, tools={"arriba": "a.tsv"})
    fusion_app.score(params)
    # only the tool part contributes: 0.5 * (1 / 1) + 0
    assert fusion.score == 0.5
    for other in fusion_app.manager.fusions[1:]:
        assert other.score == 0.0
