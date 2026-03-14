#!/usr/bin/env python
"""
Dual-RAG-Evaluator Main Entry Point

Start the application:
    python -m src.main      # Run GUI application
    python -m src.main --cli  # Run CLI application
    python -m src.main --help  # Show help
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import get_app_logger
from src.config import get_settings


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Dual-RAG-Evaluator: Compare ChromaDB vs ResonanceDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main              # Launch GUI application
  python -m src.main --cli        # Use CLI mode
  python -m src.main --test       # Run tests
  python -m src.main --version    # Show version
        """,
    )

    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode instead of GUI",
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test suite",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level",
    )

    args = parser.parse_args()

    # Configure logging
    logger = get_app_logger(level=args.log_level)
    settings = get_settings()

    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    try:
        if args.version:
            print(f"{settings.APP_NAME} v{settings.APP_VERSION}")
            print("License: MIT")
            print("Author: Srini235")
            return 0

        if args.test:
            logger.info("Running test suite...")
            import subprocess

            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                cwd=project_root,
            )
            return result.returncode

        if args.cli:
            logger.info("CLI mode not yet implemented")
            print("CLI mode coming soon!")
            return 1

        # Default: GUI mode
        logger.info("Launching GUI application...")
        from src.ui import main as gui_main

        gui_main()
        return 0

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: {e}")
        print("Ensure all dependencies are installed: pip install -r requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
