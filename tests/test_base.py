# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from mcp_servers.base import the_meaning_of_life


def test_the_meaning_of_life() -> None:
    """Test the dummy function."""
    assert the_meaning_of_life() == 42
