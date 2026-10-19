"""Only bundled runtime/modules are admitted by python313._pth."""
from pathlib import Path
import os
root = Path(__file__).resolve().parent
os.environ['TCL_LIBRARY'] = str(root / 'runtime/tcl/tcl8.6')
os.environ['TK_LIBRARY'] = str(root / 'runtime/tcl/tk8.6')
from gui import main
main()
