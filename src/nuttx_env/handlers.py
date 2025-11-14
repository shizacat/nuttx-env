"""
Handlers
"""
from dataclasses import dataclass

from . import github as gh
from . import vars


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

    def to_tag(self) -> str:
        """
        Return version in format nuttx tag repository
        """
        rc = ""
        if self.rc:
            rc = f"-{self.rc}"
        return f"nuttx-{self.version}{rc}"


# --- Handlers ---

def handle_init():
    """
    Handle init command - create empty NuttX environment
    """
    return


def handler_info():
    """
    Handler info command
    """
    # Get tags
    tags = gh.get_github_tags(
        *gh.gh_parse_url(vars.NUTTX_GITHUB_REPO)
    )

    # Convert tag to version.
    versions = [
        NuttxVersion.from_github_tag(item.name) for item in tags
    ]

    # View
    for ver in versions:
        if ver.rc is not None:
            continue
        print(ver.version, ver.to_tag())
