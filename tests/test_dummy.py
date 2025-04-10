# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from mcp_servers.dummy import dummy


def test_dummy() -> None:
    """Dummy test to ensure pytest is working."""
    assert dummy() == 42
