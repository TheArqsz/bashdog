import os
import shutil
import sys
import unittest

import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.bashdog import parsers


class TestParsers(unittest.TestCase):
    """Tests for the parsing logic in parsers.py."""

    def setUp(self):
        """Set up a temporary directory and sample file for parser tests."""
        self.test_dir = "temp_parser_test"
        os.makedirs(self.test_dir, exist_ok=True)

        self.sample_script_path = os.path.join(self.test_dir, "sample.sh")
        with open(self.sample_script_path, "w") as f:
            f.write(
                """# ============================
# @module Sample Module
# @description The main script with multiple functions.
# ============================

##!
# @description A function with a hyphenated name.
# @arg {string} $1 - A simple argument.
# @arg {boolean} [--force] - A complex argument with a
#   multi-line description.
#'
function my-cool-function() {
    echo "cool"
}
"""
            )
        self.parsers_cfg = {
            "parsers": {
                "tag_prefix": "@",
                "module": {"style": {"char": "=", "min_length": 10}},
                "function": {"start_marker": "##!", "end_marker": "#'"},
            }
        }

    def tearDown(self):
        """Clean up the temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_slugify(self):
        """Test the slugify utility function."""
        self.assertEqual(parsers.slugify("Hello World"), "hello-world")
        self.assertEqual(
            parsers.slugify("  leading-and-trailing  "), "leading-and-trailing"
        )
        self.assertEqual(parsers.slugify("Special!@#$Chars"), "specialchars")

    def test_parse_block_multiline_arg(self):
        """Test parsing a block with a multi-line argument description."""
        block_text = """
# @arg {boolean} [--force] - A complex argument with a
#   multi-line description.
"""
        parsed = parsers.parse_block(block_text, "@")
        self.assertIn("arg", parsed)
        self.assertEqual(len(parsed["arg"]), 1)
        self.assertIn("multi-line", parsed["arg"][0])

    def test_parse_block(self):
        """Test the core block parsing logic."""
        block_text = """
# @description A test description.
#   With a list:
#     - Item 1
#     - Item 2
# @arg {string} $1 - An argument.
"""
        parsed = parsers.parse_block(block_text, "@")
        self.assertIn("description", parsed)
        self.assertIn("arg", parsed)
        self.assertIn("Item 1", "".join(parsed["description"]))
        self.assertEqual(parsed["arg"][0], "{string} $1 - An argument.")

    def test_process_file_with_module(self):
        """Test processing a file that contains a module block."""
        module_data = parsers.process_file(
            self.sample_script_path, self.parsers_cfg["parsers"]
        )
        self.assertIsNotNone(module_data)
        self.assertEqual(module_data["name"], "Sample Module")
        self.assertEqual(len(module_data["functions"]), 1)
        self.assertEqual(module_data["functions"][0]["name"], "my-cool-function")
        self.assertEqual(len(module_data["functions"][0]["arg"]), 2)
