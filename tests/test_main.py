import os
import shutil
import sys
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bashdog import main as bashdog_main


class TestMain(unittest.TestCase):
    """Tests for the main orchestration and file handling logic."""

    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.test_dir = "temp_main_test"
        self.source_dir = os.path.join(self.test_dir, "scripts")
        self.output_dir = os.path.join(self.test_dir, "docs")
        os.makedirs(self.source_dir, exist_ok=True)

        self.main_script_path = os.path.join(self.source_dir, "main.sh")
        with open(self.main_script_path, "w") as f:
            f.write(
                """
# ==============================================================================
# @module Main Module
# ==============================================================================

##!
# @description A function.
#'
function sample_function() {}
"""
            )
        self.utils_path = os.path.join(self.source_dir, "utils.lib")
        with open(self.utils_path, "w") as f:
            f.write(
                """
##!
# @description A utility function.
#'
util_func() {}
"""
            )

        self.ignored_path = os.path.join(self.source_dir, "ignored-test.sh")
        with open(self.ignored_path, "w") as f:
            f.write("# This file should be excluded.")

        self.config_path = os.path.join(self.test_dir, ".bashdog.yaml")
        self.config_data = {
            "project_name": "Main Test Project",
            "source_directory": self.source_dir,
            "output_directory": self.output_dir,
            "file_extensions": [".sh", ".lib"],
            "exclude": ["*-test.sh"],
            "parsers": {
                "tag_prefix": "@",
                "module": {"style": {"char": "=", "min_length": 10}},
                "function": {"start_marker": "##!", "end_marker": "#'"},
            },
        }
        with open(self.config_path, "w") as f:
            yaml.dump(self.config_data, f)

    def tearDown(self):
        """Remove the temporary directory after tests are complete."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_find_files_and_exclusion(self):
        """Test that files are found and excluded correctly by the main logic."""
        exclude_patterns = [
            os.path.join(self.source_dir, p) for p in self.config_data["exclude"]
        ]
        found_files = list(
            bashdog_main.find_files(
                self.source_dir, self.config_data["file_extensions"], exclude_patterns
            )
        )
        self.assertIn(self.main_script_path, found_files)
        self.assertIn(self.utils_path, found_files)
        self.assertNotIn(self.ignored_path, found_files)
        self.assertEqual(len(found_files), 2)

    @patch(
        "sys.argv", ["bashdog", "--config", "temp_main_test/.bashdog.yaml", "-f", "all"]
    )
    def test_e2e_generation_with_explicit_config(self):
        """Test the full documentation generation process."""
        bashdog_main.main()
        md_path = os.path.join(self.output_dir, "documentation.md")
        html_path = os.path.join(self.output_dir, "html", "index.html")
        self.assertTrue(os.path.exists(md_path))
        self.assertTrue(os.path.exists(html_path))
        with open(md_path, "r") as f:
            self.assertIn("Module: Main Module", f.read())

    @patch(
        "sys.argv",
        ["bashdog", "-i", "temp_main_test/scripts", "-o", "temp_main_test/cli_docs"],
    )
    def test_e2e_no_config_file(self):
        """Test running the tool with only CLI arguments, no config file."""
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        bashdog_main.main()
        output_path = os.path.join(self.test_dir, "cli_docs", "documentation.md")
        self.assertTrue(os.path.exists(output_path))

    @patch("sys.argv", ["bashdog", "-f", "md", "-i", "..", "-o", "newdocs"])
    def test_e2e_config_in_cwd(self):
        """Test running the tool and finding the default .bashdog.yaml in the CWD."""
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        self.addCleanup(os.chdir, original_cwd)
        print(os.listdir(f"{original_cwd}/{self.test_dir}"))
        bashdog_main.main()
        md_path = os.path.join(
            self.output_dir.replace(f"{self.test_dir}/docs", "newdocs"),
            "documentation.md",
        )
        self.assertTrue(os.path.exists(md_path))
        with open(md_path, "r") as f:
            self.assertIn("Main Test Project", f.read())
