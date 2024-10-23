set dotenv-load

default: chainspec spawn

chainspec:
  $RUNTIMES/target/release/chain-spec-generator polkadot-local > relaychain-spec.json
  python3 patch-chainspec.py relaychain-spec.json $RUNTIMES/target/release/wbuild/polkadot-runtime/polkadot_runtime.compact.compressed.wasm

  $RUNTIMES/target/release/chain-spec-generator asset-hub-polkadot-local > assethub-spec.json
  python3 patch-chainspec.py assethub-spec.json $RUNTIMES/target/release/wbuild/asset-hub-polkadot-runtime/asset_hub_polkadot_runtime.compact.compressed.wasm

spawn:
  PATH="$PATH:$POLKADOT:$POLKADOT_PARACHAIN" zombienet spawn simple.toml --provider native

setup SDK RUNTIMES:
  #!/usr/bin/env sh
  if [ -f ".env" ]; then
    echo "Error: .env file already exists. Please remove or rename it first."
    exit 1
  fi

  echo "SDK={{SDK}}" >> .env
  echo "POLKADOT={{SDK}}/target/release/polkadot" >> .env
  echo "POLKADOT_PARACHAIN={{SDK}}/target/release/polkadot-parachain" >> .env
  echo "RUNTIMES={{RUNTIMES}}" >> .env

build:
  #!/usr/bin/env sh
  cd $RUNTIMES
  cargo b -r --features=fast-runtime --bin chain-spec-generator
  cargo b -r --features=fast-runtime -p polkadot-runtime -p asset-hub-polkadot-runtime

  cd $SDK
  cargo b -r --bin polkadot --bin polkadot-execute-worker --bin polkadot-prepare-worker --bin polkadot-parachain

  $POLKADOT --version
  $POLKADOT_PARACHAIN --version
