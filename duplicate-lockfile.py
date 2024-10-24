# Check that there are not two duplicate crates in the Cargo.lock with different versions

import toml
import sys
import os

def main():
	if len(sys.argv) != 2:
		print("Usage: python duplicate-lockfile.py <path-to-runtimes>")
		sys.exit(1)
	
	runtimes_path = sys.argv[1]
	cargo_path = os.path.join(runtimes_path, "Cargo.lock")
	cargo = toml.load(cargo_path)
	
	# Check for duplicate crates
	seen = {}
	duplicates = {}
	for package in cargo['package']:
		name = package['name']
		version = package['version']
		if name in seen:
			if seen[name] != version:
				if name not in duplicates:
					duplicates[name] = [seen[name]]
				duplicates[name].append(version)
		else:
			seen[name] = version
	
	if len(duplicates) > 0:
		print("Found duplicate crates in the Cargo.lock:")
		for name in duplicates:
			print(f"  {name}: {', '.join(duplicates[name])}")
	else:
		print("No duplicate crates found in the Cargo.lock among the {len(cargo['package'])} crates")

if __name__ == "__main__":
	main()
