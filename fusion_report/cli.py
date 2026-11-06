"""Command-line entrypoint"""

import sys

from fusion_report.app import App
from fusion_report.common.exceptions.app import AppException
from fusion_report.common.logger import Logger


def main() -> int:
    """Run fusion-report and turn known errors into a readable message and exit code 1.

    Full tracebacks are only shown with `--debug`.
    """
    debug = "--debug" in sys.argv[1:]
    try:
        app = App()
        app.build_args()
        app.run()
    except AppException as ex:
        Logger(__name__).fatal(f"Error: {ex}", exc_info=debug)
        if not debug:
            Logger(__name__).fatal("Re-run with --debug to see the full traceback.")
        return 1
    return 0
