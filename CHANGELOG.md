# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
