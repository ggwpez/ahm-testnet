# Patch the runtime of a chainspec.
#
# Usage
#   python runtime-chainspec.py para <chainspec.json> <code.wasm>
#   python runtime-chainspec.py relay <chainspec.json> <code.wasm> <para-code.wasm>

import json
import sys
import hashlib
import argparse

def main():
	args = parse_args()

	if args.subcommand == "para":
		patch_para(args.chainspec, args.code)
	elif args.subcommand == "relay":
		patch_relay(args.chainspec, args.code, args.para_code)
	else:
		print("Unknown subcommand")
		sys.exit(1)	

def patch_para(chainspec, code):
	with open(chainspec, "r") as f:
		spec = json.load(f)

	with open(code, "rb") as f:
		code = f.read()

	genesis = spec["genesis"]
	if 'runtimeGenesis' in genesis:
		genesis["runtimeGenesis"]["code"] = "0x" + code.hex()
		print("Inserted runtime (JSON)")
	else:
		genesis["raw"]["top"]["0x3a636f6465"] = "0x" + code.hex()
		print("Inserted runtime (Raw JSON)")

	with open(chainspec, "w") as f:
		json.dump(spec, f, indent=2)

def patch_relay(chainspec, code, para_code):
	with open(chainspec, "r") as f:
		spec = json.load(f)

	with open(code, "rb") as f:
		code = f.read()

	with open(para_code, "rb") as f:
		para_code = f.read()
	code_hash = hashlib.blake2b(para_code, digest_size=32).digest()

	genesis = spec["genesis"]
	if 'runtimeGenesis' in genesis:
		genesis["runtimeGenesis"]["code"] = "0x" + code.hex()
		print("Inserted runtime (JSON)")
	else:
		genesis["raw"]["top"]["0x3a636f6465"] = "0x" + code.hex()
		print("Inserted runtime (Raw JSON)")
		# Also insert para code
		key = "0xcd710b30bd2eab0352ddcc26417aa194383e6dcb39e0be0a2e6aeb8b94951ab6" + code_hash.hex()
		genesis["raw"]["top"][key] = "0x" + para_code.hex()
		print("Inserted parachain runtime (Raw JSON) with key " + key)

	with open(chainspec, "w") as f:
		json.dump(spec, f, indent=2)

def parse_args():
	parser = argparse.ArgumentParser(description="Patch the runtime of a chainspec.")
	subparsers = parser.add_subparsers(dest="subcommand", help="sub-command help")

	para_parser = subparsers.add_parser("para", help="Patch the runtime of a parachain chainspec.")
	para_parser.add_argument("chainspec", help="The parachain chainspec JSON file.")
	para_parser.add_argument("code", help="The runtime code file.")

	relay_parser = subparsers.add_parser("relay", help="Patch the runtime of a relay chain chainspec.")
	relay_parser.add_argument("chainspec", help="The relay chain chainspec JSON file.")
	relay_parser.add_argument("code", help="The runtime code file.")
	relay_parser.add_argument("para_code", help="The parachain runtime code file.")

	return parser.parse_args()

if __name__ == "__main__":
	main()
