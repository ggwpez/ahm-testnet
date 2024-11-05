## Dependencies

- [just](https://github.com/casey/just) for command running `cargo install just`.
- [zombienet](https://github.com/paritytech/zombienet/releases/) binary in your path.

## Usage

Setup, build and start the testnet with:

```sh
just
```

You should see this, wich clickable links for each network:
![img](./.assets/spawned.png)

It should also emit a lot of events for processed and enqueued messages.

## Findings

Things that came up and need adressing:
- DMP delivery fee increases once the relay starts spamming
- AH can silently ignore messages if they are too big. Need to safeguard against this on the relay side already.

## Known Issues

The test setup is quite convoluted, due to two missing dependencies:
- [ZombieBite](https://github.com/pepoviola/zombie-bite): This would allow to easily fork the network with live state.
- [Runtime stable2409](https://github.com/polkadot-fellows/runtimes/pull/490): This would hopefully make it possible to build the runtime without all the current hacks.

This results in two short-comings:
- The AssetHub initial state is empty. Therefore not having realistic PoV on the parachain side.
- The build-setup is complicated and relies on scripts to patchup and copy files - just to make cargo happy.

## Structure

This results in the following structure after running the `just` command:
- `justfile`: Central manager script with sub-commands
	- (no cmd): Setup, build and spawn the network.
	- `build`: Build the code.
	- `spawn`: Spawn the network without building.
- `runtimes`: Runtimes Polkadot runtimes from the 1.3.3 release.
- `polkadot-sdk-1.14`: Local development folder for editing SDK pallet. If you need to modify a pallet, do it there. Branch is `oty-ahm-controller`.
- `polkadot-sdk`: Don't modify this. Just used to build the nodes.
- `vendor`: The dependencies that the runtime builds against.

The code in the `runtimes` directory relies on `crates-io.patch` entries in its `Cargo.toml` file to use the dependencies from the `vendor` directory instead of from `crates.io` directly. This is needed to allow us to build against modified versions of the dependencies. The preferred way of doing this - using the 1.14 branch of the SDK - does not work here, since that branch is out of sync with `crates.io`.

This means that any modification a developer does to a pallet, for example in `polkadot-sdk-1.14/substrate/frame/balances`, will be copied by the `justfile` to the `vendor` directory. This works fine for normal code changes, but for changes to the `Cargo.toml`, it neccecitates an entry in `vendor-dep.patch`. This patch will always be applied before building.

Hopefully this graph helps to understand the relation:

![setup](.assets/setup.png)

## Strategy

The overall migration is coordinated by the `ahm-controller` pallet that is deployed on Relay and AH.

It looks like this in a linearized fashion:
`Relay on_init` -> `ahm-controller::relay_init` -> `pallet-balances::migrate_out` -> `send_xcm` -> `Ah on_init` -> `message_queue::process` -> `pallet-balances::migrate_in `.

![data-flow](.assets/data-flow.png)
