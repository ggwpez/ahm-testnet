# script to replace strings in a toml file

import sys
import re

def main():
	if len(sys.argv) != 2:
		print("Usage: python simple.py path|generator")
		sys.exit(1)

	with open("simple.toml", "r") as f:
		spec = f.read()

	if sys.argv[1] == "path":
		spec = spec.replace("chain_spec_command", "#chain_spec_command")
		spec = spec.replace("#chain_spec_path", "chain_spec_path")
		print("simple.toml: Path mode")
	elif sys.argv[1] == "generator":
		spec = spec.replace("#chain_spec_command", "chain_spec_command")
		spec = spec.replace("chain_spec_path", "#chain_spec_path")
		print("simple.toml: Generator mode")
	else:
		print("Unknown subcommand")
		sys.exit(1)
	
	# Replace multiple ## with a single
	spec = re.sub(r"#+", "#", spec)
	
	with open("simple.toml", "w") as f:
		f.write(spec)

if __name__ == "__main__":
	main()
