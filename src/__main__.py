"""Canonical CLI entry point.

Usage:
    python -m src [command] [options]

Commands:
    run         Run pipeline to a checkpoint
    branch      Create variant children from a node
    compare     Compare siblings side-by-side
    promote     Mark a node as active path

See src/cli.py for full docs, or run:
    python -m src --help
"""

from src.cli import main

main()
