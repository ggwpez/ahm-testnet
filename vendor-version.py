# Add dependencies to vendored dependencies with specific versions.
#
# Usage:
#   python3 vendor-version.py "crate:dep@version,crate2:dep2@version2..."

import argparse
import os

def main(crates):
	# Open file for append
	for crate, dep, version in crates:
		with open(f"vendor/{crate}/Cargo.toml", "a") as f:
			f.write(f"\n[dependencies.{dep}]\n")
			f.write(f"version = '{version}'\n")
			f.write("default-features = false\n")

			print(f"Added {dep} with version {version} to vendored dependencies")

def parse_args():
	parser = argparse.ArgumentParser(description="Add dependencies to vendored dependencies with specific versions.")
	parser.add_argument("dependencies", help="Dependencies to add to vendored dependencies with specific versions. Format: \"crate:dep@version,crate2:dep2@version2...\"")
	found = parser.parse_args().dependencies.split(",")
	crates = []
	for dep in found:
		crate, dep = dep.split(":")
		dep, version = dep.split("@")
		crates.append((crate, dep, version))
	return crates

if __name__ == "__main__":
	main(parse_args())
