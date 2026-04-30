"""
Methods for handlers
"""

from __future__ import annotations

import os
import zipfile
from pathlib import Path
from dataclasses import dataclass

from nuttx_env import github as gh
from nuttx_env import vars
from nuttx_env.kconfig import KConfig


@dataclass
class NuttxVersion():
    version: str
    rc: str | None = None

    @staticmethod
    def from_github_tag(tag: str) -> "NuttxVersion":
        """
        Create from github tag

        Raises
            ValueError
        """
        m = vars.pattern_nuttx_tag.match(tag)
        if m is None:
            raise ValueError("Wrong tag format")
        return NuttxVersion(version=m.group("version"), rc=m.group("rc"))

    @staticmethod
    def from_version(version: str) -> "NuttxVersion":
        """
        Create from version string
        """
        m = vars.pattern_nuttx_version.match(version)
        if m is None or m.group("version") == vars.NUTTX_VERSION_LATEST:
            raise ValueError("Wrong version format")
        return NuttxVersion(version=m.group("version"), rc=m.group("rc"))

    def to_tag(self) -> str:
        """
        Return version in format nuttx tag repository
        """
        rc = ""
        if self.rc:
            rc = f"-{self.rc}"
        return f"nuttx-{self.version}{rc}"

    def __str__(self):
        rc = ""
        if self.rc:
            rc = f"-{self.rc}"
        return f"{self.version}{rc}"


def gh_nuttx_get_tags() -> list[gh.GitHubTag]:
    """
    Retrun all tags from NuttX repository
    Order from newest to oldest
    """
    return gh.get_github_tags(*gh.gh_parse_url(vars.NUTTX_GITHUB_REPO))


def unzip_flat(zip_path: Path, extract_to: Path):
    """
    Extract zip archiv without first directory
    """
    extract_to.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            # remove first segment path (root directory)
            parts = Path(member.filename).parts
            relative = Path(*parts[1:])

            if not relative:
                continue  # skip root dir

            target = extract_to / relative

            # Extract dir or file
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())

            # --- Restore permissions ---
            # upper 16 bits contain UNIX mode
            perm = member.external_attr >> 16
            if perm != 0:
                try:
                    os.chmod(target, perm)
                except FileNotFoundError:
                    pass  # should not happen


def board_find_by_name(name: str, boards_path: Path) -> Path | None:
    """
    Find board by name in src/my-boards/<arh>/<chip>/<board name>
    Return path to board or None if not found
    """
    if not boards_path.exists():
        return None

    for arh_dir in boards_path.iterdir():
        if not arh_dir.is_dir():
            continue
        for chip_dir in arh_dir.iterdir():
            if not chip_dir.is_dir():
                continue
            for board_dir in chip_dir.iterdir():
                if not board_dir.is_dir():
                    continue
                if board_dir.name == name:
                    return board_dir

    return None


def board_get_arh_chip_from_path(board_path: Path) -> str | None:
    """
    Get architecture/chip from board path
    Place board not important
    Return  string<arh>/<chip> or None if not found
    """
    try:
        parts = board_path.resolve().parts
        if len(parts) < 3:
            return None
        arh, chip = parts[-3], parts[-2]
        return f"{arh}/{chip}"
    except ValueError:
        return None


def board_add_to_kconfig(board_name: str):
    """
    Add board to Kconfig

    Raises
        ValueError
    """
    # Get path to board
    board_path = board_find_by_name(
        board_name,
        boards_path=Path("src/nuttx/boards")
    )
    if board_path is None:
        raise ValueError(f"Board '{board_name}' not found")
    # get chip/arch
    arh_chip = board_get_arh_chip_from_path(board_path)
    if arh_chip is None:
        raise ValueError(
            "Cannot determine architecture/chip from board path")

    # Find
    kconfig = KConfig(Path("src/nuttx/boards/Kconfig"))
    kconfig.add_board(board_name, arh_chip)
