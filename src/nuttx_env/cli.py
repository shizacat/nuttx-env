import argparse
import os
import sys
from enum import StrEnum


class Commands(StrEnum):
    INIT = "init"


def args(args: list[str] | None = None) -> argparse.Namespace:
    """
    Return arguments
    """
    parser = argparse.ArgumentParser(
        description=(
            "A Python library for creating and managing "
            "project environments for RTOS NuttX."
        )
    )
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Available commands",
        required=True,
    )

    # --- Command: init ---
    cmd_init = subparsers.add_parser(
        Commands.INIT.value,
        help="Initialize empty NuttX environment in current folder"
    )

    return parser.parse_args(args)


def handle_init():
    """
    Handle init command - create empty NuttX environment
    """
    return


def main():
    """
    Main entry point for 'nuttx-env'
    """
    parsed_args = args()

    if parsed_args.command == Commands.INIT.value:
        handle_init()
    else:
        print("No command specified. Use --help for available commands.")
        sys.exit(1)
