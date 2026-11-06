# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0]

### Changed

- **SSL certificate verification is now on by default for database downloads.** Previously `-no_ssl` was passed straight to `verify=`, so verification was disabled by default (causing the `InsecureRequestWarning` seen in [#97](https://github.com/Clinical-Genomics/fusion-report/issues/97)) and only enabled when `-no_ssl` was given. `-no_ssl` now turns verification off, as documented. Users behind TLS-intercepting proxies may need to pass `-no_ssl` or set `REQUESTS_CA_BUNDLE`.
- **FusionGDB2 is now an optional source** ([#100](https://github.com/Clinical-Genomics/fusion-report/issues/100)). If it cannot be downloaded, `download` logs a warning with recovery options and still writes the other databases, and `run` skips a missing `fusiongdb2.db` with a warning. FusionGDB2 has weight 0 in the Fusion Indication Index, so scores are unaffected. COSMIC and Mitelman remain required unless disabled with `--no-*`.
- All database downloads go through a validated download path (`fusion_report/common/fetch.py`): retries with backoff for HTTP 429/5xx, timeouts, `raise_for_status`, rejection of HTML pages served instead of data, magic-byte and size checks, and atomic writes via a `.part` file. This replaces saving whatever the server returned, which caused `BadZipFile`/`KeyError: 2` crashes ([#97](https://github.com/Clinical-Genomics/fusion-report/issues/97), [#100](https://github.com/Clinical-Genomics/fusion-report/issues/100)).
- Downloads identify themselves with a `fusion-report/<version>` User-Agent instead of impersonating a browser.
- Errors are printed as a single readable message with exit code 1; add the new global `--debug` flag (`fusion_report --debug <command> ...`) for the full traceback.

### Fixed

- Fixed `--no-fusiongdb2` and `--no-mitelman` being swapped in `run` ([#99](https://github.com/Clinical-Genomics/fusion-report/issues/99)). Each flag now skips its own database, so `--no-cosmic --no-fusiongdb2` runs with Mitelman only.
- Fixed a `ZeroDivisionError` in the Fusion Indication Index when no weighted database is used (e.g. `--no-cosmic --no-mitelman`). The database part of the score is now 0 in that case ([#99](https://github.com/Clinical-Genomics/fusion-report/issues/99)).
- `run` now fails with a clear error naming the missing database file and the matching `--no-<db>` flag, instead of silently creating an empty `.db` file and failing with `no such table` ([#99](https://github.com/Clinical-Genomics/fusion-report/issues/99)).
- COSMIC (Sanger) download failures now produce an actionable error message (credentials, malformed token, missing file/version, server-side error, network/SSL) instead of only the raw HTTP error ([#97](https://github.com/Clinical-Genomics/fusion-report/issues/97)).
- The COSMIC scripted-download request now retries transient Sanger server errors (HTTP 500/502/503/504) with backoff and uses a request timeout ([#97](https://github.com/Clinical-Genomics/fusion-report/issues/97)).
- Multiple download errors are now reported one per line instead of as a Python list.
- One failing database source no longer stops the others: unexpected errors while parsing a source (e.g. pandas or zip errors) are reported per source instead of aborting `download`.
- `createdb` cleans up its temporary directory with absolute paths in a `finally` block (as `download` does since 4.1.4), keeps databases that were built successfully, and restores the working directory.
- `download` and `createdb` validate the FusionGDB2 file format (6 columns) and that the Mitelman archive contains `MBCA.TXT.DATA`, with a clear message instead of a traceback.
- Help texts: `run --no-*` now say "Do not use" (they never download), and `createdb --fusiongdb2` documents the `.txt`/`.csv` formats instead of XLSX.
- Fixed the documentation link pointing to a 404 page ([#96](https://github.com/Clinical-Genomics/fusion-report/issues/96)). The README now links to the hosted documentation at `https://clinical-genomics.github.io/fusion-report/` (and the live demo at `https://clinical-genomics.github.io/fusion-report/example/`) instead of the defunct `https://matq007.github.io/fusion-report/`.
- Replaced stale `matq007/fusion-report` repository links with `Clinical-Genomics/fusion-report` in the README (logo, CI badge), the docsify config (`docs/index.html`) and the report sidebar template.
- CI integration tests no longer download FusionGDB2 from compbio.uth.edu, which no longer serves the file to automated clients ([#100](https://github.com/Clinical-Genomics/fusion-report/issues/100)). They build FusionGDB2 from a small fixture (`tests/test_data/fusiongdb2_mini.txt`) via `createdb` instead.

### Added

- Unit tests for `App.enrich()` and `App.score()` (`tests/test_app.py`), COSMIC download handling (`tests/test_net_cosmic.py`) and the download command (`tests/test_download.py`).
- A `Unit Tests` CI workflow that runs `pytest` on every pull request.
- `--no-ssl` as an alias for `-no_ssl`.
- Troubleshooting section in `docs/download.md` (FusionGDB2 status and manual workaround with checksum, SSL, `--debug`).
- Tests for validated downloads against a local HTTP server (`tests/test_fetch.py`, `tests/test_download_sources.py`), `createdb` (`tests/test_createdb.py`) and the CLI (`tests/test_cli.py`), with small Mitelman/FusionGDB2 fixtures.

## [4.1.4]

### Fixed

- `download` no longer fails with `Directory not empty: tmp_dir`. Temporary files are handled with absolute paths and cleaned up in a `finally` block, so databases that downloaded successfully are kept even if another source fails ([#95](https://github.com/Clinical-Genomics/fusion-report/pull/95)).
- `download --qiagen` no longer crashes with a `TypeError` caused by a mismatched `get_cosmic_from_qiagen` signature ([#95](https://github.com/Clinical-Genomics/fusion-report/pull/95)).

### Changed

- The JAFFA parser supports both legacy and newer JAFFA output: `:` and `::` gene delimiters, `known` derived from `known mitelman`/`known cosmic` when the `known` column is absent, and the optional fields `geneCounts1`, `geneCounts2`, `known_mitelman`, `known_cosmic`, `cosmic_tier` and `gtex_samples` ([#95](https://github.com/Clinical-Genomics/fusion-report/pull/95)).
- The Docker image is now based on `python:3.12-slim`, installs into `/app`, and includes `procps` (needed for Nextflow task metrics) ([#95](https://github.com/Clinical-Genomics/fusion-report/pull/95)).

## [4.1.2]

### Fixed

- Fixed the broken FusionGDB2 download ([#91](https://github.com/Clinical-Genomics/fusion-report/issues/91)). The previous file `https://compbio.uth.edu/FusionGDB2/tables/FusionGDB2_id.xlsx` returns a 404 and is no longer published. The tool now downloads `https://compbio.uth.edu/FusionGDB/combined_tables/combinedFGDB2genes_genes_ID_04302024.txt`.

### Changed

- FusionGDB2 parsing now reads the new headerless 6-column TSV (using the 5'- and 3'-gene columns) instead of the old `.xlsx` export. Updated in both the `download` and `createdb` code paths.
- `createdb --fusiongdb2` now accepts a `.txt` (or pre-processed `.csv`) file instead of `.xlsx`.
- Updated the `createdb` integration test in CI to download and use the new FusionGDB2 `.txt` file.
- Updated documentation (`docs/createdb.md`, `docs/download.md`) to reference the new FusionGDB2 file and URL.
- Switched the pre-commit tooling from `pre-commit` to [`prek`](https://github.com/j178/prek): the lint CI workflow now runs `prek run --all-files`, `prek` was added to `requirements-dev.txt`, and the generated example reports under `docs/example/` are excluded from hook formatting.

### Removed

- Removed the now-unused `openpyxl` and `xlrd` dependencies (only used for the removed `.xlsx` parsing).

## [4.1.0]

### Added

- Added `createdb` command for building databases from local files, bypassing download URLs entirely
- Added integration tests: minimal tests on every PR, COSMIC tests when credentials are available (skipped on forks)
- Added more documentation

### Changed

- Updated COSMIC database API access to use the current endpoint
- Fixed file parsing to handle input formats correctly
- 4.1.1 is simply 4.1.0 but with the correct version string

### Removed

- Removed unused `sync` command ([#69](https://github.com/Clinical-Genomics/fusion-report/issues/69))

## [4.0.0]

### Added

- Added support to run the tool without SSL chain verification for users behind proxy servers who act as MITM [#79](https://github.com/Clinical-Genomics/fusion-report/pull/79)
- Added support for [CTAT-LR-Fusion](https://github.com/TrinityCTAT/CTAT-LR-fusion), which supports the fusion calling in PacBio or Nanopore long reads data [#82](https://github.com/Clinical-Genomics/fusion-report/pull/82),[#83](https://github.com/Clinical-Genomics/fusion-report/pull/83) .

### Changed

- Updated COSMIC database to be compatible with the new SANGER website[#83](https://github.com/Clinical-Genomics/fusion-report/pull/83)
- Updated project to be compatible with Python 3.12 [#83](https://github.com/Clinical-Genomics/fusion-report/pull/83)
- Updated GitHub Actions workflow to use latest actions versions [#83](https://github.com/Clinical-Genomics/fusion-report/pull/83)
- The score is now called Fusion Indication Index (FII) [#83](https://github.com/Clinical-Genomics/fusion-report/pull/83)
- FII formula changed [#83](https://github.com/Clinical-Genomics/fusion-report/pull/83):
    $$
    FII = 0.5 * \sum_{tool}^{tools provided} f(fusion, tool) + 0.5 * \sum_{db}^{dbs provided} g(fusion, db)*w(db)
    $$

    Weights for databases are as follows:

    * COSMIC (50)
    * MITELMAN (50)
    * FusionGDB2 (0)

## [3.0.0]

### Added

- Options --no-cosmic/--no-fusiongdb2/--no-mitelman to download and run without those specified databases

## [2.1.8]

### Removed

- Removed FusionGDB

## [2.1.5](https://github.com/matq007/fusion-report/releases/tag/2.1.5)

### Added

- Implemented Jaffa by [@mikewlloyd](https://github.com/mikewlloyd)

## [2.1.4](https://github.com/matq007/fusion-report/releases/tag/2.1.4)

### Fixed

- Using header columns to extract values from the fusion outputs

## [2.1.3](https://github.com/matq007/fusion-report/releases/tag/2.1.3)

### Fixed

- Missing escaping when saving a fusion page ([#34](https://github.com/matq007/fusion-report/issues/34))

## [2.1.2](https://github.com/matq007/fusion-report/releases/tag/2.1.2)

### Added

- New parameter `--allow-multiple-gene-symbols`, by default `False`

### Fixed

- Case when fusion gene symbol can't be uniquely determined and multiple fusion options are provided ([#30](https://github.com/matq007/fusion-report/issues/30))

### Changed

- renamed `tool_cutoff` to `tool-cutoff`

## [2.1.1](https://github.com/matq007/fusion-report/releases/tag/2.1.1)

### Changed

- moved databases from GitHub to Sourceforge

## [2.1.0](https://github.com/matq007/fusion-report/releases/tag/2.1.0)

### Added

- `sync` option for downloading all databases

### Changed

- all databases except `COSMIC` are now versioned in [fusion-report-db](https://github.com/matq007/fusion-report-db)

### Fixed

- Issues with downloading too many stuff ([#28](https://github.com/matq007/fusion-report/issues/28))

## [2.0.2](https://github.com/matq007/fusion-report/releases/tag/2.0.2)

### Changed

- moved from Travis to Github Actions

### Fixed

- `tool_cutoff` was not casted to `int` ([#25](https://github.com/matq007/fusion-report/issues/25))
- csv export missing data ([#26](https://github.com/matq007/fusion-report/issues/26))
- better exception handling for downloading databases

## [2.0.1](https://github.com/matq007/fusion-report/releases/tag/2.0.1)

### Fixed

- Fixed missing Mitelman database file

## [2.0.0](https://github.com/matq007/fusion-report/releases/tag/2.0.0)

This version of fusion-report has been completely rebuild from scratch following
best `python` practices as well as `typing`.

### Added

- Implemented Illumina Dragon by [@chadisaad](https://github.com/chadisaad)
- Implemented `Arriba` ([#4](https://github.com/matq007/fusion-report/issues/4))
- Export fusion list into multiple formats ([#16](https://github.com/matq007/fusion-report/issues/16))
- Version parameter ([#10](https://github.com/matq007/fusion-report/issues/10))

### Changed

- Switched `docs` to `docsify`
- Slack invite link ([#20](https://github.com/matq007/fusion-report/issues/20))
- Renamed `fusion_genes_mqc.json` to `fusions_mqc.json` ([#9](https://github.com/matq007/fusion-report/issues/9))

### Fixed

- Check if input file exists and is not empty ([#13](https://github.com/matq007/fusion-report/issues/13))

## [1.0.0](https://github.com/matq007/fusion-report/releases/tag/1.0.0) - 2019-03-26
