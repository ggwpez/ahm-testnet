set dotenv-load

default: spawn

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
  #cargo b -r --features=fast-runtime -p polkadot-runtime -p asset-hub-polkadot-runtime

  #cd $SDK
  #cargo b -r --bin polkadot --bin polkadot-execute-worker --bin polkadot-prepare-worker --bin polkadot-parachain

  $POLKADOT --version
  $POLKADOT_PARACHAIN --version
