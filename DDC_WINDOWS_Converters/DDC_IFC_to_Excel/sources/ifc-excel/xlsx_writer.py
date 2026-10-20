"""Minimal streaming XLSX writer: shared strings, no cell styles, fixed sheet order.

Rows are streamed to one temporary XML fragment per sheet; the package is
assembled once at ``save``. Cells are either numbers or shared/inline strings;
no formula element is ever written, so text such as ``=HYPERLINK(...)`` stays
inert text. The shared-string table is bounded: once ``max_shared`` unique
strings are held, further new strings are written inline.
"""
from __future__ import annotations

import os
from pathlib import Path
import uuid
import zipfile

_ESCAPE = str.maketrans({"&": "&amp;", "<": "&lt;", ">": "&gt;"})
_COLUMNS: list[str] = []


def column(index):
    """0-based column index -> Excel letters (cached)."""
    while len(_COLUMNS) <= index:
        n, letters = len(_COLUMNS) + 1, ""
        while n:
            n, rem = divmod(n - 1, 26)
            letters = chr(65 + rem) + letters
        _COLUMNS.append(letters)
    return _COLUMNS[index]


def _member(name):
    """Fixed timestamp: identical input yields a byte-identical package."""
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.compress_level = 6
    return info


def _text(value):
    text = value.translate(_ESCAPE)
    if text[:1].isspace() or text[-1:].isspace():
        return ' xml:space="preserve">' + text
    return ">" + text


class Sheet:
    __slots__ = ("title", "path", "stream", "rows", "width")

    def __init__(self, title, path):
        self.title = title
        self.path = path
        self.stream = open(path, "w", encoding="utf-8", newline="\n")
        self.rows = 0
        self.width = 0


class Workbook:
    def __init__(self, folder, max_shared=1_000_000):
        self.folder = Path(folder)
        self.sheets: list[Sheet] = []
        self.shared: dict[str, int] = {}
        self.shared_refs = 0
        self.max_shared = max_shared
        self.token = uuid.uuid4().hex

    def create_sheet(self, title):
        if len(title) > 31 or any(c in title for c in "[]:*?/\\"):
            raise ValueError("Invalid worksheet title")
        sheet = Sheet(title, self.folder / f".sheet-{self.token}-{len(self.sheets) + 1}.xml")
        self.sheets.append(sheet)
        return sheet

    def append(self, sheet, values):
        """values: sequence of None | str | int/float (numbers already validated).

        A cell carries an explicit reference only after a skipped empty cell;
        otherwise its column is implied by order (the ``r`` attribute is optional).
        """
        sheet.rows += 1
        row = str(sheet.rows)
        out = ['<row r="', row, '">']
        add = out.append
        shared = self.shared
        gap = False
        refs = 0
        for index, value in enumerate(values):
            if value is None or value == "":
                gap = True
                continue
            head = f'<c r="{column(index)}{row}"' if gap else "<c"
            gap = False
            if type(value) is str:
                number = shared.get(value)
                if number is None and len(shared) < self.max_shared:
                    number = shared[value] = len(shared)
                if number is None:
                    add(f'{head} t="inlineStr"><is><t{_text(value)}</t></is></c>')
                else:
                    refs += 1
                    add(f'{head} t="s"><v>{number}</v></c>')
            else:
                add(f'{head}><v>{value!r}</v></c>')
        self.shared_refs += refs
        if len(values) > sheet.width:
            sheet.width = len(values)
        add("</row>")
        sheet.stream.write("".join(out))

    def save(self, target, order=None):
        """Write the package to ``target`` (must not exist). ``order`` sorts sheets."""
        sheets = sorted(self.sheets, key=order) if order else list(self.sheets)
        for sheet in sheets:
            sheet.stream.close()
        target = Path(target)
        partial = target.with_name(target.name + f".partial-{self.token}")
        try:
            with zipfile.ZipFile(partial, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as package:
                n = len(sheets)
                package.writestr(_member("[Content_Types].xml"),
                                 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                                 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                                 '<Default Extension="xml" ContentType="application/xml"/>'
                                 '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                                 '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                                 '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
                                 + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, n + 1))
                                 + "</Types>")
                package.writestr(_member("_rels/.rels"),
                                 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                                 "</Relationships>")
                package.writestr(_member("xl/workbook.xml"),
                                 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                 '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                                 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                                 + "".join(f'<sheet name="{s.title.translate(_ESCAPE)}" sheetId="{i}" r:id="rId{i}"/>' for i, s in enumerate(sheets, 1))
                                 + "</sheets></workbook>")
                package.writestr(_member("xl/_rels/workbook.xml.rels"),
                                 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                 + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, n + 1))
                                 + f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                                 + f'<Relationship Id="rId{n + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>'
                                 "</Relationships>")
                package.writestr(_member("xl/styles.xml"),
                                 '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                 '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                                 '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
                                 '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
                                 '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
                                 '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
                                 '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
                                 '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
                                 "</styleSheet>")
                with package.open(_member("xl/sharedStrings.xml"), "w") as stream:
                    stream.write(('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                  f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{self.shared_refs}" uniqueCount="{len(self.shared)}">').encode())
                    chunk = []
                    for text in self.shared:
                        chunk.append(f"<si><t{_text(text)}</t></si>")
                        if len(chunk) >= 4096:
                            stream.write("".join(chunk).encode())
                            chunk.clear()
                    stream.write(("".join(chunk) + "</sst>").encode())
                for i, sheet in enumerate(sheets, 1):
                    with package.open(_member(f"xl/worksheets/sheet{i}.xml"), "w") as stream:
                        last = column(max(sheet.width, 1) - 1) + str(max(sheet.rows, 1))
                        stream.write(('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                                      '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                                      f'<dimension ref="A1:{last}"/>'
                                      '<sheetViews><sheetView workbookViewId="0"' + (' tabSelected="1"' if i == 1 else '') + '>'
                                      '<pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/>'
                                      '<selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>'
                                      '<sheetFormatPr defaultRowHeight="15"/><sheetData>').encode())
                        with open(sheet.path, "rb") as fragment:
                            while True:
                                block = fragment.read(1 << 20)
                                if not block:
                                    break
                                stream.write(block)
                        stream.write(b"</sheetData></worksheet>")
            if os.name == "nt":
                os.rename(partial, target)  # refuses an existing target
            else:
                os.link(partial, target)  # refuses an existing target
                os.unlink(partial)
        except BaseException:
            try:
                os.unlink(partial)
            except OSError:
                pass
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Close and remove this writer's own temporary sheet fragments."""
        for sheet in self.sheets:
            try:
                sheet.stream.close()
            except Exception:
                pass
            try:
                os.unlink(sheet.path)
            except OSError:
                pass
