#!/bin/bash

# ================================
# @module File Utilities
# @description
#   A collection of utility functions for handling files and directories.
#   This module demonstrates various documentation features.
#
#   Key Features:
#     - Creating directories.
#     - Checking file existence.
#     - Logging messages.
#
# @author Your Name
# ================================

##!
# @description
#   Creates a directory if it does not already exist. This function uses the
#   full 'function' keyword syntax.
#
# @arg {string} $1 - The message to log.
#                    This can also be something else.
#
# @global {array} CUSTOM_FLAG - Additional custom flags for the function.
#
# @example
#   create_directory "/tmp/my-new-folder"
#
# @returns
#   None. This function only performs an action.
#'
function create_directory() {
    local dir_path="$1"
    CUSTOM_FLAG=""
    if [ ! -d "$dir_path" ]; then
        mkdir -p "$dir_path"
        echo "Directory created: $dir_path"
    fi
}

##!
# @description
#   Checks if a file exists. This demonstrates the function syntax
#   without the 'function' keyword.
#
# @arg {string} $1 - The path to the file to check.
# @arg {string} $2 - The path to the file to check.
#
# @returns
#   0 if the file exists, 1 otherwise.
#'
file_exists() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        return 0
    else
        return 1
    fi
}

##!
# @description
#   Logs a message to the console with a timestamp. This function
#   demonstrates a name with hyphens.
#
# @global {boolean} DEBUG_MODE - If true, logs verbose messages.
#
# @arg {string} $1 - The message to log.
#
# @example
#   log-message "Initialization complete."
#
# @returns
#   None. Echos the formatted message to stdout.
#'
log-message() {
    local message="$1"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] - $message"
}
