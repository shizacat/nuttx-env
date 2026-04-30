"""
Handler for 'init' command.
"""
from __future__ import annotations

import os
from pathlib import Path
import argparse

import platformdirs

from .base import BaseHandler
from .methods import gh_nuttx_get_tags, unzip_flat, NuttxVersion
from nuttx_env.utils import regex_type_wrap
from nuttx_env import vars
from nuttx_env import github as gh
from nuttx_env import __app_name__
from nuttx_env import utils


class InitHandler(BaseHandler):
    """
    Handler for initializing a NuttX environment.
    """
    command = "init"
    command_help = "Initialize empty NuttX environment in current folder"

    def execute(self, args):
        """
        Execute the 'init' command with provided arguments.
        """
        # TODO: Add check on exists project

        # Get nuttx version
        if args.version == vars.NUTTX_VERSION_LATEST:
            version = NuttxVersion.from_github_tag(gh_nuttx_get_tags()[0].name)
        else:
            version = NuttxVersion.from_version(args.version)

        # Check archiv nuttx
        nuttx_cache_path = platformdirs.user_cache_path(
            appname=__app_name__, ensure_exists=True
        ).joinpath(
            vars.NUTTX_ARCHIV_NAME.format(version=version)
        )
        if not nuttx_cache_path.exists():
            print(f"Start downloading: {nuttx_cache_path.name}")
            utils.downloader(
                gh.gh_download_repo(
                    repo_url=vars.NUTTX_GITHUB_REPO,
                    tag=version.to_tag()
                ),
                out=nuttx_cache_path
            )
        else:
            print(f"Using cached NuttX {version}")

        # Check archiv nuttx-apps
        nuttx_apps_cache_path = platformdirs.user_cache_path(
            appname=__app_name__, ensure_exists=True
        ).joinpath(
            vars.NUTTX_APPS_ARCHIV_NAME.format(version=version)
        )
        if not nuttx_apps_cache_path.exists():
            print(f"Start downloading: {nuttx_apps_cache_path.name}")
            utils.downloader(
                gh.gh_download_repo(
                    repo_url=vars.NUTTX_APPS_GITHUB_REPO,
                    tag=version.to_tag()
                ),
                out=nuttx_apps_cache_path
            )
        else:
            print(f"Using cached NuttX Apps {version}")

        # Directory structure
        current_dir = os.getcwd()
        directories = [
            "src",
            "src/my-boards",
            "src/my-apps",
        ]
        files = [
            ("README.md", ""),
            (
                "src/.gitignore",
                (
                    "nuttx/*\n"
                    "apps/*\n"
                )
            ),
            (
                "src/my-boards/Kconfig",
                (
                    "# Kconfig for my-boards\n"
                    "\n"
                    "choice\n"
                    "\tprompt \"Select target board\"\n"
                    "\tdefault ARCH_BOARD_CUSTOM\n"
                    "\n"
                    "# ---- START USER BOARD CONFIG ----\n"
                    "# Add your board configs here\n"
                    "# ---- END USER BOARD CONFIG ----\n"
                    "\n"
                    "endchoice\n"
                    "\n"

                    "config ARCH_BOARD\n"
                    "\tstring\n"
                    "\n"
                    "# ---- START USER BOARD DEFAULT ----\n"
                    "# Set your default board here\n"
                    "# ---- END USER BOARD DEFAULT ----\n"
                    "\n"

                    "comment \"Board-Specific Options\"\n"
                    "\n"
                    "# ---- START USER BOARD OPTIONS ----\n"
                    "# Add your board-specific options here\n"
                    "# ---- END USER BOARD OPTIONS ----\n"
                )
            ),
            (
                "src/my-apps/CMakeLists.txt",
                (
                    'nuttx_add_subdirectory()\n'
                    "nuttx_generate_kconfig(MENUDESC \"My Apps\")\n"
                )
            ),
            (
                "src/my-apps/Make.defs",
                "include $(wildcard $(APPDIR)/my-apps/*/Make.defs)\n"
            ),
            (
                "src/my-apps/Makefile",
                (
                    "MENUDESC = \"My Apps\"\n"
                    "\n"
                    "include $(APPDIR)/Directory.mk"
                )
            ),
            (
                "src/my-apps/.gitignore",
                (
                    "/*.a\n"
                    "/*.dbo\n"
                    "/*.dba\n"
                    "/*.adb\n"
                    "/*.asm\n"
                    "/*.dSYM\n"
                    "/*.exe\n"
                    "/*.gcno\n"
                    "/*.gcda\n"
                    "/*.hobj\n"
                    "/*.i\n"
                    "/*.inf\n"
                    "/*.lib\n"
                    "/*.lst\n"
                    "/*.o\n"
                    "/*.wo\n"
                    "/*.obj\n"
                    "/*.rel\n"
                    "/*.src\n"
                    "/*.swp\n"
                    "/*.sym\n"
                    "/*.su\n"
                    "/*.map\n"
                    "*~\n"
                    "/.built\n"
                    "/.context\n"
                    "/.depend\n"
                    "/.kconfig\n"
                    "/*.lock\n"
                    "/Kconfig\n"
                    ".DS_Store\n"
                    "Make.dep\n"
                )
            )
        ]
        for directory in directories:
            dir_path = os.path.join(current_dir, directory)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                print(f"Created directory: {directory}")
            else:
                print(f"Directory already exists: {directory}")

        for item in files:
            file_name, content = item
            file_path = os.path.join(current_dir, file_name)
            if os.path.exists(file_path):
                print(f"File already exists: {file_name}, skipping")
                continue
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Created file: {file_name}")

        # Extract nuttx
        print(f"Start extracting: {nuttx_cache_path.name}")
        unzip_flat(nuttx_cache_path, Path("src/nuttx"))

        # Extract nuttx apps
        print(f"Start extracting: {nuttx_apps_cache_path.name}")
        unzip_flat(nuttx_apps_cache_path, Path("src/apps"))

    @classmethod
    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Add command-specific arguments to the parser.
        This method can be overridden by subclasses.
        """
        parser.add_argument(
            "--version",
            help="NuttX version",
            type=regex_type_wrap(vars.pattern_nuttx_version),
            default=vars.NUTTX_VERSION_LATEST
        )
