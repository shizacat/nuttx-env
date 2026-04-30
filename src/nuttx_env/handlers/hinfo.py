"""
Handler for 'info' command.
"""

from __future__ import annotations

import argparse

from .base import BaseHandler
from .methods import NuttxVersion, gh_nuttx_get_tags


class InfoHandler(BaseHandler):
    """
    Handler for 'info' command.
    """
    command: str = "info"
    command_help: str = "Show information about avaliable Nuttx"

    def __init__(self):
        super().__init__()

    def execute(self, args: argparse.Namespace):
        """
        Execute the 'info' command.
        """
        # Convert tag to version.
        versions = [
            NuttxVersion.from_github_tag(item.name) for item in gh_nuttx_get_tags()
        ]

        # View
        print("NuttX versions:")
        for ver in versions:
            if ver.rc is not None:
                continue
            print(" ", ver.version)
