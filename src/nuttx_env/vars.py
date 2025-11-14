"""
Stored vars
"""
import re

NUTTX_GITHUB_REPO: str = "https://github.com/apache/nuttx"
NUTTX_APPS_GITHUB_REPO: str = "https://github.com/apache/nuttx-apps"

# Patterns
REGEX_NUTTX_VERSION = r"(?P<version>\d+\.\d+\.\d+)"
REGEX_NUTTX_RC = r"(?P<rc>RC\d+)"

# Version pattern, rc options
pattern_nuttx_version = re.compile(
    rf"^{REGEX_NUTTX_VERSION}(?:-{REGEX_NUTTX_RC})$"
)
# Tags format. Examples: nuttx-12.3.0; nuttx-12.3.0-RC0
pattern_nuttx_tag = re.compile(
    rf"^nuttx-{REGEX_NUTTX_VERSION}(?:-{REGEX_NUTTX_RC})?$"
)
