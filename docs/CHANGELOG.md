# Change Log

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

See [releases](https://github.com/TUDelftGeodesy/sarxarray/releases) in the sarxarray repository for more details.

The information in this file can be generated automatically by LLM using the [release-changelog skill](.github/skills/release-changelog/SKILL.md). However, the generated content has always been reviewed and if necessary, edited by a human.

## [v1.2.3] - 2026-01-21

### Changed
- Increased metadata parsing precision.
- Added/updated tests for high-precision time parsing.

## [v1.2.2] - 2025-12-11

### Changed
- Improved scientific notation parsing in metadata readers.

### Fixed
- Lint issues fixed and release patch version bumped.

## [v1.2.1] - 2025-12-11

### Changed
- Added driver-specific unit conversion behavior.
- Added unit conversions for range sampling rate, bandwidth, and time-related fields.

## [v1.2.0] - 2025-12-10

### Added
- Additional metadata keys and orbit metadata handling.
- New tests for ARRAY keys and naming cleanup.

### Changed
- Improved metadata regulation logic for list-like inputs.
- Improved scene center coordinate handling.

### Fixed
- Unit test naming consistency and minor parser issues.

### CI
- Upgraded SonarQube scanning action.

## [v1.1.0] - 2025-07-21

### Added
- Extended metadata reading support, including Doris v4/v5 related parsing paths.
- Added API reference documentation.
- Added/expanded unit tests for metadata ingestion and parsing.

### Changed
- Standardized metadata parsing and timestamp regulation flow.
- Improved handling of inconsistent metadata sizes and coregistration naming.
- Switched xarray dimension usage from dims to sizes to avoid future warnings.

### Fixed
- Multiple linting and docstring quality issues.

### CI
- Updated SonarCloud and GitHub workflow configurations.

## [v1.0.2] - 2024-11-12

### Changed
- Updated Zenodo metadata and package version.

## [v1.0.1] - 2024-11-12

### Changed
- Patch release with package metadata/version update.

## [v1.0.0] - 2024-11-12

### Added
- Added dataset-loading path from zarr-based products (from_zarr), followed by API naming cleanup.
- Added tests around new loading functionality.

### Changed
- Renamed ambiguous variables and APIs for clarity (for example, ds to dataset, and from_zarr to from_ds in subsequent cleanup commits).
- Updated README documentation and copyright statements.
- Improved lint/test workflow by emphasizing pre-commit-based checks.

## [v0.1.2] - 2024-06-25

### Fixed
- Fixed amplitude dispersion computation for NaN pixels.
- Added unit tests and clarifying comments around NaN handling.

## [v0.1.1] - 2024-01-15

### Changed
- Documentation/badge-only patch release.

## [v0.1.0] - 2024-01-15

### Added
- Initial stable Python package release with CI, tests, linting integration, docs, and publication workflow setup.
- Added coherence and multilook-related functionality and expanded utility testing.

### Changed
- Significant documentation expansion (setup, data loading, manipulations, common operations, contributing).
- Project/package metadata updates (Zenodo, citation, organization rename, version constraints).

## Legacy Pre-SemVer Tags

### [2023.03.01] - 2023-03-03
- Alias tag to 2023.03 (no additional commits).

### [2023.03] - 2023-03-03
- Improved point selection behavior and itemsize calculation.
- Demo/data-path updates and project housekeeping.

### [2023.02] - 2023-02-07
- Early development milestone with chunk-size optimization, notebook updates, and initial refactors.
