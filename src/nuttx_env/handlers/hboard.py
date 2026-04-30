"""
Handler for 'board' command.
"""

from __future__ import annotations

import os
import argparse
from pathlib import Path

from .base import BaseHandler
from .methods import board_find_by_name, board_get_arh_chip_from_path
from nuttx_env import vars
from nuttx_env.kconfig import KConfig


class BoardHandler(BaseHandler):
    """
    Handler for 'board' command.
    """
    command: str = "board"
    command_help: str = "Manage NuttX boards"

    def execute(self, args: argparse.Namespace):
        """
        Execute the 'board' command.

        Raises:
            ValueError
        """
        if args.subcommand == "add":
            """
            Add board to NuttX environment
            """
            if args.name is None:
                raise ValueError("Board name is required for add subcommand")
            board_path = board_find_by_name(
                args.name, boards_path=vars.USER_BOARDS_DIR)
            if board_path is None:
                raise ValueError(f"Board '{args.name}' not exists")

            # Process adding board
            arh_chip = board_get_arh_chip_from_path(board_path)
            if arh_chip is None:
                raise ValueError(
                    "Cannot determine architecture/chip from board path")
            # Check target arh/chip directory
            target_board_dir = vars.NUTTX_BOARDS_DIR.joinpath(arh_chip)
            if not target_board_dir.exists():
                raise ValueError(
                    f"Architecture/chip directory not found: {target_board_dir}")

            # Create link on board in src/nuttx/boards/<arh>/<chip>/<board name>
            link_path = target_board_dir.joinpath(args.name)
            if link_path.exists():
                print(f"Board link already exists: {link_path}")
            else:
                os.symlink(
                    os.path.relpath(board_path, start=target_board_dir),
                    link_path,
                    target_is_directory=True
                )
                print(f"Created board link: {link_path} -> {board_path}")

            # Add all board Kconfig to nuttx/boards/Kconfig
            KConfig(
                kconfig_path=vars.NUTTX_BOARDS_DIR.joinpath("Kconfig")
            ).add_board()

            print(f"Board '{args.name}' added successfully")

        elif args.subcommand == "remove":
            print("Not implemented yet")
        elif args.subcommand == "list":
            """
            Handle board list subcommand
            Search boards in src/my-boards
            and apply filter <arh>/<chip>/<board name>
            """
            boards_path = Path("src/my-boards")
            if not boards_path.exists():
                print("Boards directory not found")
                return

            board_dirs: list[Path] = []
            for arh_dir in boards_path.iterdir():
                if not arh_dir.is_dir():
                    continue
                for chip_dir in arh_dir.iterdir():
                    if not chip_dir.is_dir():
                        continue
                    for board_dir in chip_dir.iterdir():
                        if not board_dir.is_dir():
                            continue
                        board_dirs.append(board_dir)

            if not board_dirs:
                print("No boards found")
                return

            print("Boards:")
            for board_dir in board_dirs:
                print(" ", board_dir.name)
        else:
            # Should not happen
            raise ValueError("Unknown subcommand")

    @classmethod
    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Add arguments for the 'board' command.
        """
        parser.add_argument(
            "subcommand",
            help="Board subcommand",
            choices=["add", "remove", "list"]
        )
        parser.add_argument(
            "--name",
            help="Board name",
            type=str,
            required=False
        )
