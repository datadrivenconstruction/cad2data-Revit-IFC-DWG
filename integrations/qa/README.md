# ddc-qa

Quality tools on top of the DDC RVT converter outputs (`elements.xlsx` + `native_graph.glb`). The converter is used as is; this package only reads its outputs.

```
pip install -e .            # numpy, openpyxl, PyYAML  (lxml only for the XSD checks in the tests)
set DDC_RVT_CLI=C:\path\to\RVTconverter.exe
```

Inputs can be an `.rvt` (converted once and cached in `%TEMP%\ddc-qa-cache`), a `*.converted` folder or an `elements.xlsx`.

## Model diff

```
ddc-qa diff old.rvt new.rvt -o out_dir
```

Elements are matched by `UniqueId` (fallback `ElementId`). Output: `diff.xlsx` (Summary, Added, Removed, Changed, Parameters old to new, Geometry), `diff.html`, `diff.glb` (green added, red removed, yellow changed, translucent grey unchanged) and `viewer.html`, a standalone page (three.js r128 from cdnjs, the GLB is embedded).

Geometry changes are read from the GLB per element: bounding box moved or resized (1 mm tolerance), mesh volume delta, triangle count. Only elements that are rows of the converter's element table are compared.

## Rule checking

```
ddc-qa check model.rvt --rules architecture mep data_quality my_rules.yaml spec.ids -o out_dir
```

Output: `check.xlsx`, `check.html`, `issues.bcfzip` (BCF 2.1, one topic per finding, viewpoint selects the `GlobalId` column as IfcGuid, camera framed on the elements). `--fail-on error|warning|info` sets the exit code.

Rule types (YAML, see `ddc_qa/rules/*.yaml`): `required_params`, `regex`, `enum`, `range`, `naming`, `duplicate` (e.g. Mark, scope model or category), `no_level`, `clash`.

Clash: elements of category lists `a` and `b` whose bounding boxes overlap by more than `tolerance` (metres) on every axis are refined by triangle-mesh intersection of the GLB geometry (numpy). If no surfaces cross, vertices of one mesh inside the other (ray parity, majority of three rays) count as containment; set `containment: false` to switch that off. Coplanar and grazing contact is not a clash. Coordinates are the GLB scene (metres, Y-up).

IDS 1.0 (buildingSMART): entity, attribute and property facets with simpleValue and xs:restriction (enumeration, pattern, bounds, length), cardinality required/optional/prohibited. A property `baseName` maps to the column of the same name (property sets are ignored, the table is flat); attributes map through `ids.ATTR_MAP` (Name to Type Name, Tag to ElementId, GlobalId, ObjectType to Family, Description). classification, material and partOf facets are not supported: such specifications are skipped and listed as notes.

## Tests

`pytest tests/test_units.py` runs on synthetic data. `tests/test_real.py` and `tests/test_check_real.py` need the DDC CLI and local sample models (they skip otherwise). BCF and IDS files are validated against the published XSDs when they are present in `C:\tmp\modern\xsd`.
