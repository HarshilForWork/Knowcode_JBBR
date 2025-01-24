import os
from pathlib import Path
import argparse

def print_directory_tree(directory, prefix="", exclude_patterns=None):
    """
    Print the directory structure in a tree-like format.
    
    Args:
        directory (str): Path to the directory to scan
        prefix (str): Prefix for the current item (used for recursion)
        exclude_patterns (list): List of patterns to exclude (e.g., ['.git', '__pycache__'])
    """
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules']
    
    # Get the directory contents
    try:
        entries = list(os.scandir(directory))
    except PermissionError:
        print(f"{prefix}├── [Permission Denied]")
        return

    # Sort entries (directories first, then files)
    entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))
    
    # Process each entry
    for i, entry in enumerate(entries):
        # Skip excluded patterns
        if any(pattern in entry.path for pattern in exclude_patterns):
            continue
            
        is_last = i == len(entries) - 1
        connector = "└──" if is_last else "├──"
        
        # Print the current entry
        print(f"{prefix}{connector} {entry.name}")
        
        # If it's a directory, recurse with updated prefix
        if entry.is_dir():
            extension = "    " if is_last else "│   "
            print_directory_tree(entry.path, prefix + extension, exclude_patterns)

def main():
    parser = argparse.ArgumentParser(description="Print directory structure in tree format")
    parser.add_argument("path", nargs="?", default=".", help="Path to directory (default: current directory)")
    parser.add_argument("--exclude", "-e", nargs="+", help="Patterns to exclude", default=[])
    args = parser.parse_args()
    
    # Resolve the absolute path
    directory = str(Path(args.path).resolve())
    
    # Add user-specified exclusions to default ones
    exclude_patterns = ['.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules'] + args.exclude
    
    print(f"\nDirectory structure for: {directory}\n")
    print_directory_tree(directory, exclude_patterns=exclude_patterns)

if __name__ == "__main__":
    main()