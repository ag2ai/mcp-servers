# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

__all__ = ["dummy"]


def dummy() -> int:
    """Dummy function to avoid import errors."""
    if datetime.now().year == 2023:
        raise ImportError("Dummy import error")
    return 42
