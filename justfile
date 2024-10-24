set dotenv-load

default: setup build spawn

setup:
  #!/usr/bin/env bash
  set -e

  # Check if psvm exists
  if ! command -v psvm 2>&1 >/dev/null; then
    cargo install --git https://github.com/paritytech/psvm psvm
  fi

  if [ ! -d "runtimes" ]; then
    echo "Cloning Polkadot Runtimes..."
    git clone https://github.com/polkadot-fellows/runtimes -q --depth 1 --branch oty-ahm-controller

    cd runtimes
    cargo update -p time
    cd -
  fi
  
  if [ ! -d "polkadot-sdk" ]; then
    echo "Cloning Polkadot SDK..."
    git clone https://github.com/paritytech/polkadot-sdk -q --depth 1 --branch master
  fi

build:
  #!/usr/bin/env sh
  set -e

  echo "Compiling the SDK ..."
  cd polkadot-sdk
  cargo b -r --bin polkadot --bin polkadot-execute-worker --bin polkadot-prepare-worker --bin polkadot-parachain
  cd -

  echo "Compiling the Runtimes ..."
  cd runtimes
  cargo b -r --features=fast-runtime --bin chain-spec-generator
  cd -

spawn:
  PATH="$PATH:polkadot-sdk/target/release" zombienet spawn simple.toml --provider native

clean:
  rm -rf polkadot-sdk polkadot-sdk-1.14 runtimes
