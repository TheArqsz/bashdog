"""
The main entry point for the bashdog documentation generator.

This script orchestrates the process of finding, parsing, and rendering
documentation for a Bash framework based on a user-provided configuration.
"""

import argparse
import fnmatch
import os
import shutil

import yaml
from jinja2 import Environment, FileSystemLoader

from . import parsers


def find_files(source_dir, extensions, exclude_patterns=None):
    """
    Find all files with given extensions, skipping any that match exclude patterns.

    Args:
        source_dir (str): The absolute path to the directory to search.
        extensions (list[str]): A list of file extensions to include (e.g., ['.sh']).
        exclude_patterns (list[str], optional): A list of glob-style patterns
            for files/directories to exclude. Defaults to None.

    Yields:
        str: The full path to a matching file.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    for root, _, files in os.walk(source_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if any(fnmatch.fnmatch(filepath, pattern) for pattern in exclude_patterns):
                continue
            if any(file.endswith(ext) for ext in extensions):
                yield filepath


def generate_docs(config, args):
    """
    Generate documentation based on the provided configuration and CLI arguments.

    Args:
        config (dict): The configuration dictionary loaded from .bashdog.yaml.
        args (argparse.Namespace): The parsed command-line arguments.
    """
    parsers_cfg = config.get("parsers", {})
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True
    )

    # Prioritize CLI arguments over config file settings
    source_dir = args.input_dir or config.get("source_directory", ".")
    output_dir = args.output_dir or config.get("output_directory", "docs")
    file_extensions = args.extensions or config.get("file_extensions", [".sh", ".bash"])

    # Combine exclude patterns from both config and CLI
    config_exclude = config.get("exclude", [])
    cli_exclude = args.exclude or []
    exclude_patterns = [
        os.path.join(source_dir, p) for p in config_exclude + cli_exclude
    ]

    if not os.path.isdir(source_dir):
        print(f"❌ Error: Source directory '{source_dir}' does not exist.")
        return

    all_modules = []
    print(f"🔍 Searching for files in '{source_dir}'...")
    for filepath in find_files(source_dir, file_extensions, exclude_patterns):
        print(f"  - Processing {filepath}...")
        module_data = parsers.process_file(filepath, parsers_cfg)
        if module_data:
            all_modules.append(module_data)

    if not all_modules:
        print("No documentation blocks found. Exiting.")
        return

    print(f"✅ Found documentation in {len(all_modules)} modules/files.")

    os.makedirs(output_dir, exist_ok=True)
    context = {
        "project_name": config.get("project_name", "Project"),
        "html_title": config.get("html_title", "Documentation"),
        "modules": all_modules,
    }

    if args.report_format in ["md", "all"]:
        md_template = env.get_template("md/documentation.md")
        with open(
            os.path.join(output_dir, "documentation.md"), "w", encoding="utf-8"
        ) as f:
            f.write(md_template.render(context))
        print("✔️ Generated Markdown documentation.")

    if args.report_format in ["html", "all"]:
        html_dir = os.path.join(output_dir, "html")
        os.makedirs(html_dir, exist_ok=True)
        html_template = env.get_template("html/base.html")
        with open(os.path.join(html_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_template.render(context))
        shutil.copy(os.path.join(template_dir, "html", "style.css"), html_dir)
        print("✔️ Generated HTML documentation.")

    print(f"🎉 All done! Your documentation is in '{output_dir}'.\n")


def main():
    """
    Parse command-line arguments and run the documentation generator.
    """
    parser = argparse.ArgumentParser(
        description="Bash Documentation Generator (bashdog)",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--input",
        dest="input_dir",
        help="Path to the source directory to scan. Required if no config file is used.",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="report_format",
        choices=["html", "md", "all"],
        default="md",
        help="The output format for the documentation (default: md).",
    )
    parser.add_argument(
        "--config",
        default=".bashdog.yaml",
        help="Path to the configuration file (default: .bashdog.yaml)",
    )

    override_group = parser.add_argument_group(
        "Configuration Overrides",
        "These arguments override settings from the .bashdog.yaml file.",
    )
    override_group.add_argument(
        "-o", "--output", dest="output_dir", help="Specify the output directory."
    )
    override_group.add_argument(
        "--extensions",
        nargs="+",
        help="A space-separated list of file extensions to process (e.g., .sh .bash).",
    )
    override_group.add_argument(
        "--exclude",
        nargs="+",
        help="A space-separated list of glob patterns to exclude.",
    )

    args = parser.parse_args()

    config = {}
    if os.path.exists(args.config):
        print(f"🛠️ Found config in '{args.config}'...")
        with open(args.config, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    elif not args.input_dir:
        print(
            "❌ Error: A config file is required, or you must specify an input directory with -i/--input."
        )
        parser.print_help()
        return

    generate_docs(config, args)


if __name__ == "__main__":
    main()
