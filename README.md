<p align="center">
    <img src="https://github.com/TheArqsz/bashdog/blob/main/assets/bashdog_logo.png?raw=true" alt="bashdog Logo" width="30%"/>
</p>
<p align="center">
    <code>bashdog = bashdoc + ng</code>
</p>



# bashdog

A modern, configurable, and easy-to-use documentation generator for Bash frameworks. bashdog parses structured comments in your shell scripts and generates clean, readable documentation in both Markdown and HTML formats.

Inspired by [bashdoc](https://github.com/dustinknopoff/bashdoc) but I needed something a bit different that suited my needs better.

## Features

- **Module & Function Documentation** - Group related functions into modules for better organization.
- **Highly Configurable** - Control parsing behavior, file discovery, and output using a simple `.bashdog.yaml` file. No need to touch the code.
- **CLI Overrides** - All key configuration options can be overridden directly from the command line for maximum flexibility.
- **Multiple Output Formats** - Generate documentation in Markdown, HTML, or both.
- **File Exclusion** - Easily exclude test files, vendor directories, or drafts from the documentation.
- **Minimal Dependencies** - Built with a small set of Python libraries.

## Examples

You can find some generated examples in the [examples/](examples/) directory.

## Installation

Ensure you have Python 3 installed. You can install `bashdog` directly from the project root using pip.

```bash
cd /path/to/bashdog
pip install .
```

or

```bash
pip install git+https://github.com/TheArqsz/bashdog.git
```

...or just use [Docker version](#usage-with-docker).

This will make the `bashdog` command available in your terminal.

## Usage

You can run `bashdog` using a configuration file, command-line arguments, or a combination of both.

### Quick Start

1. Create a `.bashdog.yaml` file in the root of your Bash project (see the configuration section below for an example).
2. Update the source_directory in `.bashdog.yaml` to point to your scripts.
3. Run the tool:

```
bashdog
```

By default, this will generate a `documentation.md` file in a `./docs` directory.

### Usage with Docker

You can also run `bashdog` using the pre-built Docker image, which avoids the need for a local Python installation.

1. Pull the image from Docker Hub:

```bash
docker pull thearqsz/bashdog:latest
```

2. Run the container - the key is to mount your project directory into the container's `/app` working directory and use proper user id.

```bash
docker run --rm -v "$(pwd)":/app -u $(id -u) thearqsz/bashdog:latest
```

This command runs bashdog inside the container using the `.bashdog.yaml` file from your current directory. The generated docs/ folder will be created in your local project directory.

You can also pass command-line arguments:

```bash
docker run --rm -v "$(pwd)":/app -u $(id -u) thearqsz/bashdog:latest -i ./scripts -o ./output -f all
```

### Command-Line Arguments

For a full list of options, run `bashdog --help`.

```bash
usage: bashdog [-h] [-i INPUT_DIR] [-f {html,md,all}] [--config CONFIG] [-o OUTPUT_DIR] [--extensions EXTENSIONS [EXTENSIONS ...]]
               [--exclude EXCLUDE [EXCLUDE ...]]

Bash Documentation Generator (bashdog)

options:
  -h, --help            show this help message and exit
  -i INPUT_DIR, --input INPUT_DIR
                        Path to the source directory to scan. Required if no config file is used.
  -f {html,md,all}, --format {html,md,all}
                        The output format for the documentation (default: md).
  --config CONFIG       Path to the configuration file (default: .bashdog.yaml)

Configuration Overrides:
  These arguments override settings from the .bashdog.yaml file.

  -o OUTPUT_DIR, --output OUTPUT_DIR
                        Specify the output directory.
  --extensions EXTENSIONS [EXTENSIONS ...]
                        A space-separated list of file extensions to process (e.g., .sh .bash).
  --exclude EXCLUDE [EXCLUDE ...]
                        A space-separated list of glob patterns to exclude.

```

### Configuration File ([.bashdog.yaml](.bashdog.yaml))

This is the recommended way to use `bashdog`. Create a `.bashdog.yaml` file in your project root. The sample is below but you can find [full `.bashdog.yaml` example](.bashdog.yaml) in the root of this project.

```yaml
project_name: "My Awesome Bash Project"

parsers:
  tag_prefix: "@"
  
  module:
    style:
      char: "="
      min_length: 10
  
  function:
    start_marker: "##!"
    end_marker: "#'"
```

## Documentation Syntax

`bashdog` parses two types of documentation blocks: modules and functions.

### Module Documentation

A module block provides high-level information about a script file. It is enclosed by separator lines defined in your `.bashdog.yaml`.

```bash
# ==============================================================================
# @module My Awesome Module
# @description
#   This module handles all the file processing operations. It provides
#   functions to read, write, and validate file formats.
#
#   Key features include:
#     - Reading CSV files.
#     - Writing JSON output.
#
# @author John Doe
# ==============================================================================
```

### Function Documentation

A function block describes a single function. It begins with a start_marker (`##!`) and can optionally end with an end_marker (`#'`). The block must be placed directly before the function definition.

```bash
##!
# @description
#   Reads a CSV file from the given path and returns its content.
#   This is a multi-line description that will be joined into a
#   single paragraph.
#
# @arg {string} $1 - The full path to the input CSV file.
#
# @global {boolean} VERBOSE - If true, prints extra logging.
#
# @example
#   read_csv "/path/to/my/data.csv"
#'
function read_csv() {
  local file_path="$1"
  # ... function logic ...
}
```

### Supported Tags:

- `@description`: A description of the module or function. Can be multi-line.
- `@arg`: Describes a function argument. Format: `{type} $name - Description`.
- `@global`: Describes a global variable the function uses. Format: `{type} VAR_NAME - Description`.
- `@example`: A code example showing how to use the function.
- `@author`: The author of a module.
- `@usage`: Usage information for a module.

## Development

To set up a development environment:

1. Clone the repository.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install the package:

```bash
pip install .
```

This allows you to make changes to the source code and test them immediately without reinstalling.

## Tests

To run the test suite, navigate to the project's root directory and execute the following command:

```bash
python -m unittest discover tests
```

This will automatically discover and run all tests located in the [tests/](tests/) directory.

## License

This project is licensed under the [MIT License](LICENSE).

## Logo Attribution

The logo used for the **bashdog** project was designed and generated with the assistance of Gemini, a large language model developed by Google.