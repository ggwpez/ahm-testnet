default: setup snapshot build spawn

setup:
  #!/usr/bin/env bash
  set -ex

  mkdir -p tmp

  # Build a custom version of PDU locally to not overwrite the system-wide one
  if [ ! -d "tmp/pdu/target/release/pdu" ]; then
    cd tmp
    echo "Installing PDU locally..."
    if [ ! -d "pdu" ]; then
      git clone https://github.com/ggwpez/pdu --branch oty-chainspec --depth 1 -q
    fi
    cd pdu
    cargo build -r -q --features chainspec
    cd ../..
  fi

  if [ ! -d "tmp/venv" ]; then
    echo "Setting up Python venv..."
    cd tmp
    python3 -m venv venv
    tmp/venv/bin/python3 -m pip install toml cargo_workspace
    cd ..
  fi

  if [ ! -d "polkadot-sdk-1.14" ]; then
    echo "Cloning Polkadot-SDK 1.14..."
    git clone https://github.com/paritytech/polkadot-sdk -q --depth 1 --branch oty-ahm-controller polkadot-sdk-1.14
    # This is the 1.14 base commit, need it to diff against it later
    cd polkadot-sdk-1.14
    git fetch origin 237767ac911486b573fb3fd2ec7273bfbc9fc1f8 --depth 1
    cd ..
  fi

  if [ ! -d "runtimes" ]; then
    echo "Cloning Runtimes..."
    git clone https://github.com/polkadot-fellows/runtimes -q --depth 1 --branch oty-ahm-controller

    echo "Setting up runtimes..."
    cd runtimes
    cargo update -p time -q

    cargo vendor ../vendor -q
    cd ../vendor

    git init -b master .
    git add .
    git commit -m "Init" --author "ahm <test@test.com>" --no-verify --no-gpg-sign --no-signoff || true
    cd ..
    tmp/venv/bin/python3 patch-crates.py vendor runtimes
    echo "Runtimes cloned and patched"
  fi

  if [ ! -d "polkadot-sdk" ]; then
    echo "Cloning Polkadot SDK..."
    git clone https://github.com/paritytech/polkadot-sdk -q --depth 1 --branch master
  fi

  # Install a local version of try-runtime-cli in case that the system-wide one is the wrong version or does not exist.
  if [ ! -d "tmp/try-runtime-cli" ]; then
    echo "Installing try-runtime CLI locally..."
    cd tmp
    git clone https://github.com/paritytech/try-runtime-cli --depth 1 -q
    cd try-runtime-cli
    cargo build -r -q
  fi

snapshot:
  #!/usr/bin/env sh

  if [ ! -f "tmp/polkadot.snap" ]; then
    echo "Taking Polkadot snapshot..."
    tmp/try-runtime-cli/target/release/try-runtime create-snapshot --uri wss://try-runtime.polkadot.io:443 tmp/polkadot.snap
  fi

build:
  #!/usr/bin/env sh
  set -e

  cd vendor
  # Only checkout rust files, since we manually change the toml files
  git checkout -- "*/**/*.rs"
  cd ..
  tmp/venv/bin/python3 vendor.py --repo-root polkadot-sdk-1.14 --vendor-dir vendor

  echo "Compiling the SDK ..."
  cd polkadot-sdk
  #cargo b -r --bin polkadot --bin polkadot-execute-worker --bin polkadot-prepare-worker --bin polkadot-parachain -q
  cd -

  echo "Compiling the Runtimes ..."
  cd runtimes
  cargo b -r --features=fast-runtime --bin chain-spec-generator -q
  cd -

  # Switch our zombienet from path to chainspec generator:
  echo "Preparing the chain specs..."
  python3 switch-simple.py generator

  # First time we run only to generate the chain specs, so kill it early.
  rm -rf ./my-zombienet
  tmp/venv/bin/python3 grep.py "Clear Boot Nodes" zombienet spawn simple.toml --provider native -d my-zombienet --force

  cp my-zombienet/asset-hub-polkadot-local-1000-polkadot-local.json tmp/ah-local.json
  cp my-zombienet/polkadot-local.json tmp/polkadot-local.json
  rm -rf ./my-zombienet

  echo "Inserting genesis keys..."
  tmp/pdu/target/release/pdu chainspec --snapshot-path tmp/polkadot.snap -c tmp/polkadot-local.json --chainspec-out-path tmp/polkadot-local-patched.json  --pallets System,Vesting,Balances,Indices
  # --dev-accounts 100000

  # Switch our zombienet from chainspec generator to chain spec path:
  tmp/venv/bin/python3 switch-simple.py path

spawn:
  export PATH="$PATH:polkadot-sdk/target/release"
  zombienet spawn simple.toml --provider native

clean:
  rm -rf tmp
