## Dependencies

- [just](https://github.com/casey/just) for command running `cargo install just`.
- [zombienet](https://github.com/paritytech/zombienet/releases/) binary in your path.
- `polkadot` and `polkadot-parachain` binaries in your path. See setup below.

## Usage

First setup the `.env` file to contain the correct file paths for your system:
```sh
just setup ../path-to-polkadot-sdk ../path-to-runtimes
```

Then build the node, runtime and chain-spec-generator:
```sh
just build
```

Finally, launch the network with:
```sh
just
```

You should see this, wich clickable links for each network:
![img](./.assets/spawned.png)

The Asset Hub will only produce after the first era passed (2 minutes).
