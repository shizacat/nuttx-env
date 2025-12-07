"""
Work with Kconfig files
kconfig-language.txt in the NuttX tools repository.

"""

from pathlib import Path


class KConfig:
    """
    Class for working with Kconfig files
    """

    def __init__(self, kconfig_path: Path):
        self._kconfig_path = kconfig_path

    def add_board(self, board_name: str, arh_chip: str) -> None:
        """
        Add board to Kconfig file
        
        Raise
            ValueError: if cannot find place to insert new board
        """
        board_def = f"ARCH_BOARD_{board_name.upper().replace('-', '_')}"
        lines = self._load()

        lineno: int = self._find_first_place_to_insert(lines)

        # insert new board, #37
        part = f"\tdefault \"{board_name}\""
        lines.insert(
            lineno,
            f"{part}{" " * (37 - len(part))}if {board_def}\n"
        )
        
        # insert board-specific options
        lineno = self._find_second_place_to_insert(lines)
        lines.insert(lineno, f"if {board_def}\n")
        lines.insert(lineno + 1, f"source \"boards/{arh_chip}/{board_name}/Kconfig\"\n")
        lines.insert(lineno + 2, "endif\n")

        # save Kconfig file
        with self._kconfig_path.open("w") as kconfig_file:
            kconfig_file.writelines(lines)

    def _load(self) -> list[str]:
        """
        Load Kconfig file, put lines to list and return it
        """
        with self._kconfig_path.open("r") as kconfig_file:
            return kconfig_file.readlines()

    def _find_first_place_to_insert(self, lines: list[str]) -> int:
        """
        Find first place to insert new board

        Raise
            ValueError: if place not found

        Return line number or None if not found
        """
        lineno: int | None = None
        step1 = False
        for idx, line in enumerate(lines):
            if not step1 and not line.startswith('config ARCH_BOARD'):
                continue
            step1 = True
            if not line.startswith('comment "Common Board Options"'):
                continue
            lineno = idx - 1
            break
        if lineno is None:
            raise ValueError("Cannot find first place to insert board")
        return lineno

    def _find_second_place_to_insert(self, lines: list[str]) -> int:
        """
        Find second place to insert new board

        Raise
            ValueError: if place not found

        Return line number or None if not found
        """
        lineno: int | None = None
        step1 = False
        for idx, line in enumerate(lines):
            if not step1 and not line.startswith('comment "Board-Specific Options"'):
                continue
            step1 = True
            if not line.startswith('comment "Board-Common Options"'):
                continue
            lineno = idx - 1
            break
        if lineno is None:
            raise ValueError("Cannot find second place to insert board")
        return lineno
