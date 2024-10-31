#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import tempfile
from cargo_workspace import Workspace
from pathlib import Path
from typing import Dict, List, Set, Tuple

class RustVendorPatcher:
    def __init__(self, repo_root: str, vendor_dir: str):
        self.repo_root = Path(repo_root)
        self.workspace = Workspace.from_path(repo_root)
        self.vendor_dir = Path(vendor_dir)

    def get_modified_files(self) -> List[Path]:
        """Get list of modified files in the git repository."""
        result = subprocess.run(
            ['git', 'diff', '--name-only', '237767ac911486b573fb3fd2ec7273bfbc9fc1f8'],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        return [Path(f) for f in result.stdout.splitlines() if f.strip()]
    
    def modified_by_crate(self) -> Dict[str, List[Path]]:
        """Get modified files grouped by crate."""
        crate_files: Dict[str, List[Path]] = {}
        for file in self.get_modified_files():
            found_crate_path = ""
            found_crate_name = None

            for crate in self.workspace.crates:
                path = os.path.dirname(crate.rel_path)
                if path_is_parent(path, file):
                    if len(path) > len(found_crate_path):
                        found_crate_path = path
                        found_crate_name = crate.name
            
            if found_crate_name:
                if found_crate_name not in crate_files:
                    crate_files[found_crate_name] = []
                rel_to_crate = os.path.relpath(file, found_crate_path)
                crate_files[found_crate_name].append(Path(rel_to_crate))
            else:
                print(f"Could not find crate for file: {file}")

        return crate_files
    
    def copy_files(self, crate_files: Dict[str, List[Path]]):
        """Copy the modified files into their respective crate dir."""
        copied_files: Dict[str, Path] = {}
        for crate_name, files in crate_files.items():
            for file in files:
                from_path = os.path.dirname(self.workspace.crates.find_by_name
                (crate_name).abs_path) / file
                to_path = self.vendor_dir / crate_name / file
                print(f"Copying {from_path} to {to_path}")
                to_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(from_path, to_path)

def path_is_parent(parent_path, child_path):
    # Smooth out relative path names, note: if you are concerned about symbolic links, you should use os.path.realpath too
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    # Compare the common path of the parent and child path with the common path of just the parent path. Using the commonpath method on just the parent path will regularise the path name in the same way as the comparison that deals with both paths, removing any trailing path separator
    return os.path.commonpath([parent_path]) == os.path.commonpath([parent_path, child_path])

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Patch Rust vendor dependencies based on repository changes')
    parser.add_argument('--repo-root', type=str, default='.', help='Path to repository root')
    parser.add_argument('--vendor-dir', type=str, default='vendor', help='Path to vendor directory')
    
    args = parser.parse_args()
    
    patcher = RustVendorPatcher(args.repo_root, args.vendor_dir)
    paths = patcher.modified_by_crate()
    print(paths)
    patcher.copy_files(paths)

if __name__ == '__main__':
    main()
