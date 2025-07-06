# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-07-06

### Added

- Initial release of bashdog.
- Core functionality to parse structured comments from Bash files.
- Support for both Module and Function level documentation blocks.
- Generation of documentation in Markdown and HTML formats.
- Configuration via a central .bashdog.yaml file.
- User-friendly parser configuration using simple start/end markers and styles instead of regex.
- Command-line interface (CLI) for running the generator.
- CLI arguments to override .bashdog.yaml settings (--input, --output, --format, --extensions, --exclude).
- The .bashdog.yaml file is optional (default values are defined).
- Support for excluding files and directories using glob patterns.
- Generated HTML includes a clickable Table of Contents (TOC) for improved navigation.
- Generated Markdown includes a Table of Contents (TOC).
- The tool can be run as a module with python -m bashdog.
- Project structure including README.md, LICENSE, .gitignore, and a CI workflow for GitHub Actions.
- Test suite using unittest to ensure code quality and stability.
- The default output format for the CLI is md (Markdown).

### Changed

None

### Fixed

- Corrected a parser bug that failed to read content from multi-line tags like @description.
- Fixed an issue where not all documentation blocks in a file were being detected.
- Ensured that leading/trailing whitespace and newlines are correctly stripped from parsed values.
- Resolved a bug where intentionally formatted lists in comments were not preserved.
- Fixed an issue where pip would not include template files during installation by updating pyproject.toml.
