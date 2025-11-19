#!/usr/bin/env python3
import argparse
import math
import sys
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class RollupProfile:
    key: str
    name: str
    description: str
    proof_gas: int
    calldata_gas_per_tx: int
    overhead_gas_per_batch: int


PROFILES: Dict[str, RollupProfile] = {
    "aztec": RollupProfile(
        key="aztec",
        name="Aztec-style zk rollup",
        description=(
            "Privacy-preserving zk rollup with relatively expensive proofs but "
            "efficient calldata packing."
        ),
        proof_gas=900_000,
        calldata_gas_per_tx=320,
        overhead_gas_per_batch=60_000,
    ),
    "zama": RollupProfile(
        key="zama",
        name="Zama-style FHE + rollup hybrid",
        description=(
            "Conceptual profile for a system combining fully homomorphic "
            "encryption with rollup-style batching. Proofs are cheaper but "
            "ciphertexts are larger."
        ),
        proof_gas=500_000,
        calldata_gas_per_tx=700,
        overhead_gas_per_batch=70_000,
    ),
    "soundness": RollupProfile(
        key="soundness",
        name="Soundness-first research rollup",
        description=(
            "Profile that prioritizes simple, auditable circuits and extra "
            "safety margins over raw gas efficiency."
        ),
        proof_gas=650_000,
        calldata_gas_per_tx=420,
        overhead_gas_per_batch=90_000,
    ),
}


def wei_from_gwei(x: float) -> int:
    return int(x * 1_000_000_000)


def eth_from_wei(x: int) -> float:
    return x / 1_000_000_000_000_000_000


def list_profiles() -> None:
    print("Available profiles:")
    for key, prof in PROFILES.items():
        print(f"- {key}: {prof.name}")
    print("")
    print("Use --profile with one of the keys above, or 'custom' to provide your own parameters.")


def compute_cost(
    profile: RollupProfile,
    tx_count: int,
    batch_size: int,
    gas_price_gwei: float,
) -> Dict[str, Any]:
    if tx_count <= 0:
        raise ValueError("tx_count must be positive.")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive.")

    batches = math.ceil(tx_count / batch_size)

    total_proof_gas = batches * profile.proof_gas
    total_overhead_gas = batches * profile.overhead_gas_per_batch
    total_calldata_gas = tx_count * profile.calldata_gas_per_tx
    total_gas = total_proof_gas + total_overhead_gas + total_calldata_gas

    gas_price_wei = wei_from_gwei(gas_price_gwei)
    total_fee_wei = total_gas * gas_price_wei
    total_fee_eth = eth_from_wei(total_fee_wei)

    per_tx_gas = total_gas / tx_count
    per_tx_fee_eth = total_fee_eth / tx_count

    return {
        "profile": profile.key,
        "profileName": profile.name,
        "description": profile.description,
        "txCount": tx_count,
        "batchSize": batch_size,
        "batches": batches,
        "gasPriceGwei": gas_price_gwei,
        "proofGasPerBatch": profile.proof_gas,
        "calldataGasPerTx": profile.calldata_gas_per_tx,
        "overheadGasPerBatch": profile.overhead_gas_per_batch,
        "totalProofGas": total_proof_gas,
        "totalOverheadGas": total_overhead_gas,
        "totalCalldataGas": total_calldata_gas,
        "totalGas": total_gas,
        "perTxGas": per_tx_gas,
        "totalFeeEth": total_fee_eth,
        "perTxFeeEth": per_tx_fee_eth,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="rollup_cost_profiler",
        description=(
            "Offline rollup gas and fee estimator for Web3 projects inspired by "
            "Aztec, Zama, and soundness-focused designs."
        ),
    )
    parser.add_argument(
        "tx_count",
        type=int,
        help="Number of transactions you plan to batch.",
    )
    parser.add_argument(
        "--profile",
        choices=list(PROFILES.keys()) + ["custom"],
        default="aztec",
        help="Which profile to use (default: aztec).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=256,
        help="Number of transactions per batch (default: 256).",
    )
    parser.add_argument(
        "--gas-price-gwei",
        type=float,
        default=20.0,
        help="Gas price in gwei (default: 20).",
    )
    parser.add_argument(
        "--proof-gas",
        type=int,
        help="Custom proof gas per batch (required when --profile custom).",
    )
    parser.add_argument(
        "--calldata-gas-per-tx",
        type=int,
        help="Custom calldata gas per transaction (required when --profile custom).",
    )
    parser.add_argument(
        "--overhead-gas-per-batch",
        type=int,
        help="Custom overhead gas per batch (required when --profile custom).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a human summary.",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List known profiles and exit.",
    )
    return parser.parse_args()


def build_custom_profile(args: argparse.Namespace) -> RollupProfile:
    missing = []
    if args.proof_gas is None:
        missing.append("--proof-gas")
    if args.calldata_gas_per_tx is None:
        missing.append("--calldata-gas-per-tx")
    if args.overhead_gas_per_batch is None:
        missing.append("--overhead-gas-per-batch")
    if missing:
        print("❌ Missing required options for custom profile: " + ", ".join(missing))
        sys.exit(1)

    return RollupProfile(
        key="custom",
        name="Custom rollup profile",
        description="User-defined gas parameters for a hypothetical rollup.",
        proof_gas=args.proof_gas,
        calldata_gas_per_tx=args.calldata_gas_per_tx,
        overhead_gas_per_batch=args.overhead_gas_per_batch,
    )


def print_human(summary: Dict[str, Any]) -> None:
    print("🔍 Rollup cost estimate")
    print(f"Profile      : {summary['profileName']} ({summary['profile']})")
    print(f"Description  : {summary['description']}")
    print("")
    print(f"Transactions : {summary['txCount']}")
    print(f"Batch size   : {summary['batchSize']}")
    print(f"Batches      : {summary['batches']}")
    print(f"Gas price    : {summary['gasPriceGwei']:.2f} gwei")
    print("")
    print("Gas breakdown (units of gas):")
    print(f"  Proof gas per batch      : {summary['proofGasPerBatch']}")
    print(f"  Overhead gas per batch   : {summary['overheadGasPerBatch']}")
    print(f"  Calldata gas per tx      : {summary['calldataGasPerTx']}")
    print("")
    print(f"  Total proof gas          : {summary['totalProofGas']}")
    print(f"  Total overhead gas       : {summary['totalOverheadGas']}")
    print(f"  Total calldata gas       : {summary['totalCalldataGas']}")
    print(f"  Total gas                : {summary['totalGas']}")
    print("")
    print("Cost estimate:")
    print(f"  Total fee   : {summary['totalFeeEth']:.6f} ETH")
    print(f"  Per tx fee  : {summary['perTxFeeEth']:.8f} ETH")
    print(f"  Per tx gas  : {summary['perTxGas']:.2f} gas")


def main() -> None:
    args = parse_args()

    if args.list_profiles:
        list_profiles()
        return

    if args.profile == "custom":
        profile = build_custom_profile(args)
    else:
        profile = PROFILES[args.profile]

    try:
        summary = compute_cost(
            profile=profile,
            tx_count=args.tx_count,
            batch_size=args.batch_size,
            gas_price_gwei=args.gas_price_gwei,
        )
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    if args.json:
        import json

        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print_human(summary)


if __name__ == "__main__":
    main()
