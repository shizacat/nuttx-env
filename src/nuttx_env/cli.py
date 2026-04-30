"""
NuttX Environment CLI
"""

import argparse
import sys

from .handlers.base import BaseHandler


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

    for slcs in BaseHandler.__subclasses__():
        slcs.register_subparser(subparsers)

    return parser.parse_args(args)


def main():
    """
    Main entry point for 'nuttx-env'
    """
    parsed_args = args()

    try:
        handler = BaseHandler.get_handler_by_command(parsed_args.command)
    except (KeyError, ValueError):
        print("No command specified. Use --help for available commands.")
        sys.exit(1)

    # Call handler
    try:
        handler(args=parsed_args)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
