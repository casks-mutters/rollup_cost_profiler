# rollup_cost_profiler

A tiny offline CLI tool for estimating gas and fee costs for rollup-style Web3 systems.  
It is inspired by ecosystems like Aztec (zk rollups), Zama (FHE based computation), and soundness focused protocol labs.

The repository contains exactly two files:
- app.py
- README.md


## Overview

rollup_cost_profiler helps you answer questions such as:

- How much gas will my Aztec style zk rollup batch consume for a given number of transactions?
- What is the approximate total and per transaction fee at a given gas price?
- How do different design philosophies (Aztec, Zama, soundness first) compare in terms of gas footprint?
- What happens if I tweak batch size or calldata gas?

The tool does not talk to any blockchain or RPC endpoint. It is purely a calculator that encodes a few rough, illustrative profiles related to Web3 and privacy oriented designs.


## Profiles

The script comes with three built in profiles:

aztec  
Represents a privacy preserving zk rollup with relatively expensive proofs but efficient calldata.

zama  
Represents a conceptual FHE and rollup hybrid, inspired by Zama, where ciphertexts are larger and calldata costs are higher.

soundness  
Represents a soundness first rollup design that favors simple, auditable circuits and extra safety margins over raw efficiency.

You can also supply your own custom parameters via the custom profile option.


## Installation

Requirements:

- Python 3.10 or newer.

Steps:

1. Create a new GitHub repository with any name.
2. Place app.py and this README.md in the root of the repository.
3. Ensure python is on your PATH (python or python3).
4. No external dependencies are required; the script uses only the standard library.


## Usage

Basic estimate using the Aztec style profile:

python app.py 1000

Use the Zama style profile with a different gas price:

python app.py 2000 --profile zama --gas-price-gwei 35

Use the soundness oriented profile and a smaller batch size:

python app.py 500 --profile soundness --batch-size 64

List available profiles:

python app.py 1 --list-profiles

Note that tx_count is still required even when listing profiles, but the script will exit after showing the list.


## Custom profile

If you want full control over the parameters, use the custom profile and specify all required flags:

python app.py 1500 --profile custom --batch-size 256 --gas-price-gwei 25 --proof-gas 800000 --calldata-gas-per-tx 500 --overhead-gas-per-batch 70000

Custom profile fields:

- proof-gas: gas used per batch for the proof itself.
- calldata-gas-per-tx: gas used per transaction for calldata.
- overhead-gas-per-batch: extra gas per batch for bookkeeping and protocol overhead.


## JSON output

If you want to integrate the tool into scripts or dashboards, you can request JSON output:

python app.py 1000 --profile aztec --json

The JSON payload includes:

- profile and profileName
- description
- txCount, batchSize, batches
- gasPriceGwei
- proofGasPerBatch, calldataGasPerTx, overheadGasPerBatch
- totalProofGas, totalOverheadGas, totalCalldataGas, totalGas
- perTxGas
- totalFeeEth, perTxFeeEth


## Expected output

Human readable mode prints:

- A short header with the selected profile and description.
- A section with transaction count, batch size, and gas price.
- A gas breakdown showing proof, overhead, calldata, and total gas.
- A cost estimate with total fee and per transaction fee in ETH.

Values are approximations and meant for intuition building, not for production level financial planning.


## Relation to Web3, Aztec, Zama, and soundness

While the tool does not connect to a chain, the profiles are inspired by real themes in the Web3 ecosystem:

- Aztec style designs emphasize zero knowledge proofs and private transactions on top of Ethereum.
- Zama style ideas involve fully homomorphic encryption and encrypted compute, which affect calldata size and cost.
- Soundness driven labs emphasize formal verification, simple circuits, and conservative parameters.

By playing with these profiles and custom settings, you can quickly get an intuition for how design choices in privacy, soundness, and cryptography might translate into gas and fee trade offs.


## Notes

- Numbers used in profiles are illustrative, not exact measurements from any production network.
- Always consult real gas measurements and off chain tooling when planning actual deployments.
- You are encouraged to fork this repository and adjust the profiles to match your own rollup, L2, or privacy protocol.
