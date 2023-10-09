#!/bin/bash

script_dir=$(dirname "$0")

# Function to display help message
display_help() {
    echo "Usage: $0 <path_to_json_abi_folder>"
    echo
    echo "This script requires the path to the folder containing JSON ABI files for IHyperdrive as its argument."
    echo
    echo "Options:"
    echo "  -h, --help        Display this help message and exit."
    echo
}

# Check if no arguments or help flag is provided
if [ "$#" -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    display_help
    exit 0
fi

# Create the hypertypes folder if it does not already exist
target_dir="$script_dir/../hypertypes"
if [ ! -d "$target_dir" ]; then
    mkdir -p "$target_dir"
    touch "$target_dir/__init__.py"
fi

# Loop recursively over all .json files in the provided directory and run the python script for each
find "$1" -type f -name "*.json" | while read -r json_file; do
    echo $json_file
    python lib/pypechain/pypechain/run_pypechain.py "$json_file" "$target_dir" "120"
done
