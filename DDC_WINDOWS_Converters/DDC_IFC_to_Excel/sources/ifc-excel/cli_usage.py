"""Command line front door. Imports no Tk: ``--help`` must never open a window."""
import sys

HELP_FLAGS = ("--help", "-h", "/?", "-?", "/h", "/help")


def product_version():
    try:
        import converter
        return converter.VERSION
    except Exception:
        return "development"


def usage(program="IFC to Excel", version=None):
    version = version or product_version()
    return f"""DDC IFC to Excel {version}
Converts IFC / IFCZIP models to Excel workbooks (.xlsx) on this computer.

Usage:
  "{program}"                          open the window
  "{program}" FILE_OR_FOLDER [...]     open the window with these files added
  "{program}" FILE [FILE ...] --output FOLDER [--raw-tables]
                                       convert without a window, one JSON line per file
  "{program}" --help | -h | /?         print this text and exit

Options:
  --output FOLDER   where the job folders are written (required for headless mode)
  --raw-tables      also write the raw Entities / SourceReals sheets and data.jsonl
  --help, -h, /?    show this help

Exit status: 0 on success, 1 when a file could not be converted, 2 for wrong usage.
Community edition - free, no registration required. https://datadrivenconstruction.io
"""


def wants_help(argv):
    return any(arg.lower() in HELP_FLAGS for arg in argv)


def split_arguments(argv):
    """Return (files, output, raw, unknown)."""
    files, output, raw, unknown = [], None, False, []
    items = list(argv)
    while items:
        arg = items.pop(0)
        if arg == "--output" or arg.startswith("--output="):
            if arg == "--output":
                output = items.pop(0) if items else None
                if output is None:
                    unknown.append("--output (value missing)")
            else:
                output = arg.split("=", 1)[1]
        elif arg == "--raw-tables":
            raw = True
        elif arg.startswith("-") and len(arg) > 1:
            unknown.append(arg)
        else:
            files.append(arg)
    return files, output, raw, unknown


def run(argv, stdout=None, stderr=None):
    """Handle help and headless conversion. Return an exit code, or None to start the GUI."""
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    if wants_help(argv):
        stdout.write(usage())
        stdout.flush()
        return 0
    if not argv:
        return None
    files, output, raw, unknown = split_arguments(argv)
    if unknown or (output is not None and not files) or (output is None and not files):
        stderr.write("Unknown or incomplete arguments: " + (", ".join(unknown) or " ".join(argv)) + "\n\n" + usage())
        return 2
    if output is None:
        return None  # Files only: the window opens with them in the list.
    import converter
    status = 0
    for source in files:
        extra = ["--raw-tables"] if raw else []
        if converter.main([source, "--output", output, *extra]) != 0:
            status = 1
    return status
