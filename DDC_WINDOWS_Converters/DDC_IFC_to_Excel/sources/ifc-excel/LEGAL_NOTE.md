# Legal note — IFC schema data (simplified mode)

**Status: engineering reasoning, not legal advice. LAWYER TO CONFIRM.**

## Issue

The buildingSMART IFC EXPRESS schema publications (IFC2X3, IFC4, IFC4X3) are
licensed CC BY-ND 4.0. The earlier reader (`ifc-independent/model.py` with
`schemas/generated/*.json`, produced by `schema_gen.py`) shipped entity and
type metadata mechanically generated from those files. Whether such generated
tables are "adapted material", which CC BY-ND does not allow to be shared, is
unresolved (see `packaging/ifc-excel/licenses.json`, earlier flag "DO NOT SHIP until resolved").

## Decision (owner, 2026-10-16)

IFC to Excel and DDC Viewer use a simplified mode that neither ships nor loads
any data generated from the EXPRESS schemas:

1. `ifc-independent/core_model.py` is a generic ISO 10303-21 (STEP physical
   file) reader. It keeps each entity's type name as written in the input file
   and its raw positional attribute list. The STEP file syntax is an ISO
   standard and is not part of the buildingSMART schema publications.
2. A small table, written by hand in our own code, names the attributes of the
   core entities we interpret: spatial tree, names, property sets, quantities,
   materials, units, styles, placements and geometry. It is limited to publicly
   known class and attribute names in positional order. It contains no schema
   text, definitions, WHERE rules, types or generated inheritance graph. A few
   "is also a" answers are hand-written rules based on name patterns and
   attribute shapes in the file.
3. Every other entity is exported generically: its type name as written in the
   file, its STEP id and raw attributes `Attr1..AttrN`. Nothing is invented and
   nothing is filled in by default; unresolved values stay empty.
4. `model.py`, `reader.py`, `schema_gen.py` and `schemas/` are not imported by
   the IFC to Excel runtime and are excluded from packaging (the build refuses
   them: `tools/prepare_ifc_portable.py`). They may remain only as developer
   tools and test oracles, not shipped.
5. The product still names "IFC" and IFC class names to describe the data it
   reads (descriptive, nominative use). "IFC" and "buildingSMART" are
   trademarks of buildingSMART International Ltd.; the notices say so.

## Questions for counsel

- Is a hand-written list of public class / attribute names, independently
  authored, free of the CC BY-ND restriction? We assume yes (facts and names;
  no expression copied).
- Is reading a file that conforms to the schema, and writing out its own type
  names, unaffected by the schema licence? We assume yes.
- Does any trademark or attribution wording still need to be included?
