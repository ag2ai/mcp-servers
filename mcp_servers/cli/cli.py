# Copyright (c) 2023 - 2025, AG2ai, Inc., AG2ai open-source projects maintainers and core contributors
#
# SPDX-License-Identifier: Apache-2.0

from logging import getLogger
from typing import Annotated, Optional

import typer

from ..__about__ import __version__

app = typer.Typer(rich_markup_mode="rich")
# app.add_typer(
#     docker_app,
#     name="docker",
#     help="[bold]Docker[/bold] commands for [bold]FastAgency[/bold]",
# )


logger = getLogger(__name__)


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__version__}")
        raise typer.Exit()


@app.callback()
def callback(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", help="Show the version and exit.", callback=version_callback
        ),
    ] = None,
) -> None:
    """mcp-servers CLI - The [bold]mcp-servers[/bold] command line app. 😎

    Generate and manage your [bold]mcp-servers[/bold].

    Read more in the docs: [link]https://ag2ai.github.io/mcp-servers/latest/[/link].
    """  # noqa: D415


@app.command(help="Display the version of mcp-servers")
def version() -> None:
    typer.echo(__version__)


@app.command(help="Generate MCP servers")
def gen() -> None:
    typer.echo("Generate mcp servers")


def main() -> None:
    app()
