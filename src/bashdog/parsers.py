"""
Core parsing logic for the bashdog documentation generator.

This module is responsible for opening and reading source files, identifying
documentation blocks for modules and functions based on user-defined markers,
and transforming these blocks into structured data.
"""

import os
import re

FUNCTION_SYNTAX_REGEX = re.compile(r"^\s*(?:function\s+)?([\w-]+)\s*\(\)\s*\{")

ARG_SYNTAX_REGEX = re.compile(
    r"\{(?P<type>\w+)\}\s+(?P<name>.+?)\s+-\s+(?P<desc>.*)", re.IGNORECASE
)
GLOBALS_SYNTAX_REGEX = ARG_SYNTAX_REGEX  # Reuse the same regex for globals


def slugify(text):
    """
    Create a simple, URL-friendly slug from a string.

    This is used to generate unique HTML IDs for linking.

    Args:
        text (str): The input string to convert.

    Returns:
        str: A lowercase, hyphenated, URL-safe string.
    """
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text


def is_styled_marker(line, style_config):
    """
    Check if a line matches a defined marker style (e.g., '=========').

    Args:
        line (str): The line of text to check.
        style_config (dict): A dictionary containing 'char' and 'min_length' keys.

    Returns:
        bool: True if the line matches the style, False otherwise.
    """
    if (
        not style_config
        or "char" not in style_config
        or "min_length" not in style_config
    ):
        return False
    if not line.startswith("#"):
        return False
    content = line[1:].strip()
    return len(content) >= style_config["min_length"] and all(
        c == style_config["char"] for c in content
    )


def parse_block(text_block, tag_prefix):
    """
    Parse a documentation text block into a dictionary of tags and values.

    This function handles multi-line values, preserving indented
    lines (like lists) as newlines and joining non-indented lines as single
    paragraphs.

    Args:
        text_block (str): The raw string content of a documentation block.
        tag_prefix (str): The character that identifies a tag (e.g., '@').

    Returns:
        dict: A dictionary where keys are tags and values are the parsed content.
    """
    doc = {}
    current_tag = None
    lines = [line.lstrip("#") for line in text_block.strip().split("\n")]

    for line in lines:
        stripped_line = line.strip()
        # Check if the line starts a new tag
        if stripped_line.startswith(tag_prefix):
            parts = stripped_line[len(tag_prefix) :].split(maxsplit=1)
            current_tag = parts[0]
            value = parts[1].strip() if len(parts) > 1 else ""
            # If the tag already exists, it's a multi-value tag like @arg.
            if current_tag in doc:
                # Ensure it's a list before appending.
                if not isinstance(doc[current_tag], list):
                    doc[current_tag] = [doc[current_tag]]
                value = value.lstrip()
                if (
                    value
                    and (value[0].islower() or value[0] == ",")
                    and len(doc[current_tag]) > 0
                ):
                    # If the value starts with a lowercase letter or comma,
                    # we treat it as a continuation of the previous tag.
                    doc[current_tag][-1] += " " + value
                else:
                    doc[current_tag].append(value)
            else:
                # It's the first time we see this tag.
                # This is joined to string in templates
                doc[current_tag] = [value]

        # This line is a continuation of the previous tag's content.
        elif current_tag in doc:
            last_item_index = len(doc[current_tag]) - 1
            # Check for indentation to preserve formatting.
            if current_tag == "arg" and line and line[0].isspace():
                # This covers multiline args.
                doc[current_tag][last_item_index] += " " + stripped_line
            # Check for indentation to preserve formatting.
            elif line and line[0].isspace():
                # This covers cases like lists or paragraphs.
                doc[current_tag][last_item_index] += "\n" + stripped_line
            elif line == "":
                # If the line is empty, we just add a new line to the last item.
                doc[current_tag][last_item_index] += "\n"
            else:
                doc[current_tag][last_item_index] += " " + stripped_line

    return doc


def format_function_data(parsed_block, function_name, module_id):
    """
    Structure the parsed data specifically for a function.

    Args:
        parsed_block (dict): The dictionary returned by parse_block.
        function_name (str): The name of the function being documented.

    Returns:
        dict: A formatted dictionary containing all function documentation.
    """
    func_data = {
        "name": function_name,
        "id": slugify(f"{module_id}-{function_name}"),
        "description": parsed_block.get("description", ""),
        "arg": [],
        "globals": [],
        "example": parsed_block.get("example", ""),
        "returns": parsed_block.get("returns", ""),
    }

    for arg_str in parsed_block.get("arg", []):
        match = ARG_SYNTAX_REGEX.match(arg_str)
        if match:
            data = match.groupdict()
            func_data["arg"].append(
                {
                    "name": data["name"].strip(),
                    "type": data["type"].strip(),
                    "description": data["desc"].strip(),
                }
            )

    for global_str in parsed_block.get("global", []):
        match = GLOBALS_SYNTAX_REGEX.match(global_str)
        if match:
            data = match.groupdict()
            func_data["globals"].append(
                {
                    "name": data["name"].strip(),
                    "type": data["type"].strip(),
                    "description": data["desc"].strip(),
                }
            )
    return func_data


def format_module_data(parsed_block):
    """
    Structure the parsed data specifically for a module.

    Args:
        parsed_block (dict): The dictionary returned by parse_block.

    Returns:
        dict: A formatted dictionary containing all module documentation.
    """
    if "module" in parsed_block:
        parsed_block["name"] = "".join(parsed_block.pop("module")).strip()

    if "name" in parsed_block:
        parsed_block["id"] = slugify("".join(parsed_block["name"])).strip()

    return parsed_block


def process_file(filepath, parsers_cfg):
    """
    Open and process a single file, extracting all documentation.

    This function orchestrates the parsing of a single source file, first
    looking for a module block and then for all associated function blocks.

    Args:
        filepath (str): The full path to the file to process.
        parsers_cfg (dict): The parser configuration from the main config file.

    Returns:
        dict or None: A dictionary containing all documentation for the file,
        or None if no documentation was found.
    """
    tag_prefix = parsers_cfg.get("tag_prefix", "@")
    module_style_cfg = parsers_cfg.get("module", {}).get("style")
    func_cfg = parsers_cfg.get("function", {"start_marker": "##!", "end_marker": "#'"})

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Process Module Block
    module_info = {}
    module_info.setdefault("name", os.path.basename(filepath))
    module_info.setdefault("id", slugify(os.path.basename(filepath)))
    in_module_block = False
    module_buffer = []
    for line in lines:
        stripped_line = line.strip()
        if is_styled_marker(stripped_line, module_style_cfg):
            if not in_module_block:
                in_module_block = True
            else:
                module_info = format_module_data(
                    parse_block("\n".join(module_buffer), tag_prefix)
                )
                break
        elif in_module_block:
            module_buffer.append(line)

    module_name = module_info.get("name")
    base_filename = os.path.basename(filepath)

    if module_name:
        module_info["id"] = slugify(f"{base_filename}-{module_name}")

    module_info["functions"] = []

    # Process Functions
    doc_buffer = None

    for line in lines:
        stripped = line.strip()
        is_start_marker = stripped == func_cfg.get("start_marker")
        is_end_marker = func_cfg.get("end_marker") and stripped == func_cfg.get(
            "end_marker"
        )
        function_match = FUNCTION_SYNTAX_REGEX.match(line)

        # Case 1: A function is found.
        if function_match:
            # If we have a documentation block buffered from previous lines, process it.
            if doc_buffer is not None:
                function_name = function_match.group(1)
                parsed = parse_block("".join(doc_buffer), tag_prefix)
                formatted = format_function_data(
                    parsed, function_name, module_info["id"]
                )
                module_info["functions"].append(formatted)
            doc_buffer = None
            continue

        # Case 2: A new documentation block starts.
        if is_start_marker:
            doc_buffer = [line]
            continue

        # Case 3: We are inside an active documentation block.
        if doc_buffer is not None:
            # If we hit the end marker, we stop appending, but keep the buffer
            # ready for the upcoming function definition.
            if not is_end_marker:
                doc_buffer.append(line)

    if module_info.get("description") or module_info["functions"]:
        return module_info
    return None
