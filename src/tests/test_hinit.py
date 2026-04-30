"""
Tests for InitHandler.
"""
from __future__ import annotations

import argparse
from unittest.mock import patch

import pytest

from nuttx_env.handlers.hinit import InitHandler
from nuttx_env.handlers.methods import NuttxCommit, NuttxVersion
from nuttx_env import vars
from nuttx_env.github import GitHubTag


def _ns(**kwargs) -> argparse.Namespace:
    defaults = {
        "version": vars.NUTTX_VERSION_LATEST,
        "nuttx_commit": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# --- Tests ---

class TestGetNuttxVersion:
    """Tests for InitHandler._get_nuttx_version."""

    def test_explicit_version_without_commit(self):
        handler = InitHandler()
        ver, commit = handler._get_nuttx_version(_ns(version="12.3.0"))

        assert commit is None
        assert ver == NuttxVersion(version="12.3.0", rc=None)

    def test_explicit_version_with_rc(self):
        handler = InitHandler()
        ver, commit = handler._get_nuttx_version(_ns(version="12.3.0-RC1"))

        assert commit is None
        assert ver == NuttxVersion(version="12.3.0", rc="RC1")

    @patch("nuttx_env.handlers.hinit.gh_nuttx_get_tags")
    def test_latest_resolves_first_github_tag(self, mock_tags):
        mock_tags.return_value = [
            GitHubTag(name="nuttx-12.4.0"),
            GitHubTag(name="nuttx-12.3.0"),
        ]
        handler = InitHandler()
        ver, commit = handler._get_nuttx_version(
            _ns(version=vars.NUTTX_VERSION_LATEST)
        )

        assert commit is None
        assert ver == NuttxVersion(version="12.4.0", rc=None)
        mock_tags.assert_called_once()

    def test_with_nuttx_commit(self):
        handler = InitHandler()
        ver, commit = handler._get_nuttx_version(
            _ns(version="12.3.0", nuttx_commit="abcdef0123456")
        )

        assert ver == NuttxVersion(version="12.3.0", rc=None)
        assert commit == NuttxCommit(commit="abcdef0123456")

    def test_invalid_commit_raises_value_error(self):
        handler = InitHandler()
        with pytest.raises(ValueError, match="Wrong commit hash format"):
            handler._get_nuttx_version(
                _ns(version="12.3.0", nuttx_commit="short")
            )
