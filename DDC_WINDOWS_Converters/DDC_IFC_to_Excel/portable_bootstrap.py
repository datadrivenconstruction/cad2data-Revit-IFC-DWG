"""Only bundled runtime/modules are admitted by python313._pth."""
from pathlib import Path
import os
import sys

root = Path(__file__).resolve().parent
os.environ['TCL_LIBRARY'] = str(root / 'runtime/tcl/tcl8.6')
os.environ['TK_LIBRARY'] = str(root / 'runtime/tcl/tk8.6')
import cli_usage

code = cli_usage.run(sys.argv[1:])  # --help, -h, /? and headless conversion never open a window
if code is not None:
    sys.exit(code)
from gui import main
sys.exit(main(sys.argv[1:]))
