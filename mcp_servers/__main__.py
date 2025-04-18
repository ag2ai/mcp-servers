# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

"""CLI entry point for the mcp-servers package."""

import warnings

from .cli import app as cli

warnings.filterwarnings("default", category=ImportWarning, module="mcp_servers")

if __name__ == "__main__":
    cli(prog_name="mcp-severs")
