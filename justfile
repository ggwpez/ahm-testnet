set dotenv-load

default: chainspec spawn

chainspec:
  $RUNTIMES/target/release/chain-spec-generator polkadot-local > relaychain-spec.json
  python3 patch-chainspec.py relaychain-spec.json ../runtimes/target/release/wbuild/polkadot-runtime/polkadot_runtime.compact.compressed.wasm

  $RUNTIMES/target/release/chain-spec-generator asset-hub-polkadot-local > assethub-spec.json
  python3 patch-chainspec.py assethub-spec.json ../runtimes/target/release/wbuild/asset-hub-polkadot-runtime/asset_hub_polkadot_runtime.compact.compressed.wasm

spawn:
  zombienet spawn simple.toml --provider native

setup SDK RUNTIMES:
  if [ -f ".env" ]; then
    echo "Error: .env file already exists. Please remove or rename it first."
    exit 1
  fi

  SDK="{{SDK}}" >> .env
  RUNTIMES="{{RUNTIMES}}" >> .env

build:
  cd RUNTIMES && cargo b -r --features fast-runtime -p polkadot-runtime -p asset-hub-polkadot-runtime && cargo b -r --bin chain-spec-generator
