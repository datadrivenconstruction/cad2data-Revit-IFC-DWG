# Fixtures

* `ifc_duplex_excerpt/` - not shipped in this repository (tests that need it are skipped). Build one with
  `make_ifc_excerpt.py` from the output of DDC IFC to Excel on an IFC file you may use; the same rows exist as
  `data.jsonl`, `data.sqlite` and `drawing.xlsx`.
* `rvt_properties/properties.jsonl` — the row layout of `properties.jsonl` from RVT Converter 0.6.8
  (`--properties`, schema `native_stored_properties/2`) with invented values for four elements. It is not
  cut from a real model: the models available for testing are not ours to redistribute.
* `ifc_duplex_excerpt_v2/data.jsonl` (not shipped) - "version 2" of the excerpt for `ddc diff`: the same real records with the
  edits a designer makes between two issues (two elements removed, two added, four modified, two with a new STEP id
  and the same GlobalId). Made by `make_ifc_excerpt_v2.py`; the edited values are not converter output.
