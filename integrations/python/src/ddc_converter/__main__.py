import argparse
import json
import sys

from . import ConverterError, convert, download_cli


def main(argv=None):
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="ddc-convert", description="Convert a Revit file with the DDC converter.")
    ap.add_argument("input", nargs="?")
    ap.add_argument("-f", "--formats", default="xlsx,glb", help="comma list: glb,xlsx,csv,ifc,gltf,obj,sqlite,all")
    ap.add_argument("-o", "--out")
    ap.add_argument("--upload", help="s3://, gs:// or az:// prefix to receive the output folder")
    ap.add_argument("--download", action="store_true", help="download the CLI into ~/.ddc-converter and exit")
    a = ap.parse_args(argv)
    if a.download:
        try:
            print(download_cli())
        except ConverterError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        return 0
    if not a.input:
        ap.error("input required")
    try:
        r = convert(a.input, a.formats.split(","), a.out, upload=a.upload)
    except ConverterError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(r.to_dict(), indent=2))
    return 0 if r.ok else (r.exit_code or 1)


if __name__ == "__main__":
    sys.exit(main())
