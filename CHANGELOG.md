# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## dev

### FIX

- `tool_cutoff` was not casted to `int` ([#25](https://github.com/matq007/fusion-report/issues/25))
- csv export missing data ([#26](https://github.com/matq007/fusion-report/issues/26))
- better exception handling for downloading databases

## [2.0.1](https://github.com/matq007/fusion-report/releases/tag/2.0.1)

### FIX

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
