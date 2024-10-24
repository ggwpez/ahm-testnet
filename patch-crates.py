# Patch all dependencies of the runtimes repo to a local Polkadot SDK folder.
#
# Usage
#  python3 patch-crates.py <path-to-sdk> <path-to-runtimes>

import tomllib
import sys
import os

def main():
	if len(sys.argv) != 3:
		print("Usage: python runtime-chainspec.py <path-to-sdk> <path-to-runtimes>")
		sys.exit(1)
	
	sdk_path = sys.argv[1]
	runtimes_path = sys.argv[2]

	if not os.path.exists(sdk_path):
		print(f"Error: {sdk_path} does not exist")
		sys.exit(1)
	if not os.path.exists(runtimes_path):
		print(f"Error: {runtimes_path} does not exist")
		sys.exit(1)
	
	# Recursively loop through all Cargo.toml files and record their name and path
	sdk_crates = {}
	for root, dirs, files in os.walk(sdk_path):
		for file in files:
			if file == "Cargo.toml":
				path = os.path.join(root, file)
				with open(path, "rb") as f:
					parsed = tomllib.load(f)
					if 'package' in parsed:
						# Cut off the file name
						path = os.path.dirname(path)
						sdk_crates[parsed['package']['name']] = os.path.relpath(path, runtimes_path)
	
	print(f"Found {len(sdk_crates)} crates in the SDK")
	# Go through all workspace.dependencies of the runtimes Cargo.toml and add a patch entry to the end
	patches = []

	with open(os.path.join(runtimes_path, "Cargo.toml"), "rb") as f:
		runtimes = tomllib.load(f)
		for name in runtimes['workspace']['dependencies']:
			dep = runtimes['workspace']['dependencies'][name]
			
			if name in sdk_crates:
				patches.append(f"{name} = {{ path = \"{sdk_crates[name]}\" }}")
	
	# Append the patches to the Cargo.toml
	with open(os.path.join(runtimes_path, "Cargo.toml"), "a") as f:
		f.write("\n[patch.crates-io]\n")
		f.write("\n".join(patches))		

if __name__ == "__main__":
	main()