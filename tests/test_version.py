# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

import mcp_servers


def test_version() -> None:
    assert mcp_servers.__version__ is not None  # type: ignore[attr-defined]
