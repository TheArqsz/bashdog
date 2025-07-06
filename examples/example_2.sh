#!/bin/bash

# ================================
# @module Edge Case Examples
# @description
#   This script is designed to show edge cases for the bashdog parser.
#
#   It includes:
#     - Functions with no documentation.
#     - Documentation blocks that are empty or have missing tags.
#     - Functions with special characters in their names.
#     - Multi-line example blocks.
#
# @author John Doe
# ================================

##!
# @description
#   A standard, well-formed function to establish a baseline.
# @arg {string} $1 - The input value.
# @returns {string} The processed value.
#'
function standard-function() {
    echo "Input was: $1"
}

# This function has no documentation block at all.
# The parser should ignore it completely.
function undocumented_function() {
    echo "I should not appear in the docs."
}

##!
# @description A function with an underscore in its name.
#'
function _internal_helper() {
    echo "Internal helper"
}

##!
# @description
#   This function has a multi-line example.
# @example
#   # First, set a variable
#   VAR="hello"
#   # Then, run the function
#   run_complex_example "$VAR"
#'
run_complex_example() {
    echo "Example with var: $1"
}

##!
# @description This block is empty.
#'
function function_with_empty_doc() {
    echo "This function has an empty doc block above it."
}

##!
# @description This function has a returns tag with no description.
# @returns
#'
function function_with_empty_return_tag() {
    return 0
}
