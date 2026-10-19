"""Conservative derived views; all source definitions remain separate."""
from collections import defaultdict, Counter
from itertools import chain
from contextlib import closing
import json
import math
import re
from decimal import Decimal, localcontext, Inexact, Rounded, InvalidOperation, Overflow, Underflow

PREFIX = {None: 1., "EXA": 1e18, "PETA": 1e15, "TERA": 1e12, "GIGA": 1e9,
          "MEGA": 1e6, "KILO": 1e3, "HECTO": 1e2, "DECA": 1e1, "DECI": 1e-1,
          "CENTI": 1e-2, "MILLI": 1e-3, "MICRO": 1e-6, "NANO": 1e-9,
          "PICO": 1e-12, "FEMTO": 1e-15, "ATTO": 1e-18}
KINDS = {"LENGTHUNIT": ("METRE", 1, "m"), "AREAUNIT": ("SQUARE_METRE", 2, "m2"),
         "VOLUMEUNIT": ("CUBIC_METRE", 3, "m3")}
MEASURES = {"IfcLengthMeasure": "LENGTHUNIT", "IfcPositiveLengthMeasure": "LENGTHUNIT",
            "IfcNonNegativeLengthMeasure": "LENGTHUNIT", "IfcAreaMeasure": "AREAUNIT", "IfcVolumeMeasure": "VOLUMEUNIT"}
QUANTITIES = {"IfcQuantityLength": ("LENGTHUNIT", "LengthValue"),
              "IfcQuantityArea": ("AREAUNIT", "AreaValue"), "IfcQuantityVolume": ("VOLUMEUNIT", "VolumeValue")}

# Exact powers from SI definitions, never reconstructed from binary64 factors.
PREFIX_EXPONENT = {None: 0, 'EXA': 18, 'PETA': 15, 'TERA': 12, 'GIGA': 9,
                   'MEGA': 6, 'KILO': 3, 'HECTO': 2, 'DECA': 1, 'DECI': -1,
                   'CENTI': -2, 'MILLI': -3, 'MICRO': -6, 'NANO': -9,
                   'PICO': -12, 'FEMTO': -15, 'ATTO': -18}
MAX_EXACT_DIGITS = 2048
MAX_EXACT_EXPONENT = 4096
MAX_EXACT_UNIT_DEPTH = 32


def _bounded_decimal(number):
    if (not number.is_finite() or len(number.as_tuple().digits) > MAX_EXACT_DIGITS
            or abs(number.as_tuple().exponent) > MAX_EXACT_EXPONENT
            or (number and abs(number.adjusted()) > MAX_EXACT_EXPONENT)):
        raise ValueError('Exact decimal resource/finite limit')
    return number


def _source_decimal(node):
    """Only literal source tokens/integers; a rounded float is not provenance."""
    if type(node) is int:
        if node.bit_length() > MAX_EXACT_DIGITS * 4:
            raise ValueError('Exact integer resource limit')
        return _bounded_decimal(Decimal(node))
    if not isinstance(node, dict) or set(node) != {'step_real'}:
        raise ValueError('Exact numeric source token unavailable')
    token = node['step_real']
    if (not isinstance(token, str) or len(token) > 128
            or not re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[Ee][+-]?[0-9]+)?', token)):
        raise ValueError('Invalid exact REAL source token')
    return _bounded_decimal(Decimal(token))


def _exact_product(left, right):
    _bounded_decimal(left); _bounded_decimal(right)
    if len(left.as_tuple().digits) + len(right.as_tuple().digits) > MAX_EXACT_DIGITS:
        raise ValueError('Exact multiplication digit budget')
    with localcontext() as context:
        context.prec = MAX_EXACT_DIGITS
        context.Emax, context.Emin = MAX_EXACT_EXPONENT, -MAX_EXACT_EXPONENT
        for signal in (Inexact, Rounded, InvalidOperation, Overflow, Underflow):
            context.traps[signal] = True
        return _bounded_decimal(left * right)


def unit_scale_exact(unit, kind, visited=frozenset()):
    """Exact declared SI/conversion factors, with bounded arithmetic and depth."""
    if (unit is None or unit.id() in visited or len(visited) >= MAX_EXACT_UNIT_DEPTH
            or getattr(unit, 'UnitType', None) != kind):
        raise ValueError('Missing, cyclic, too-deep or incompatible exact unit')
    expected, power, _ = KINDS[kind]
    if unit.is_a('IfcSIUnit'):
        if unit.Name != expected or unit.Prefix not in PREFIX_EXPONENT:
            raise ValueError('Unsupported exact SI declaration')
        return Decimal('1E' + str(PREFIX_EXPONENT[unit.Prefix] * power))
    if unit.is_a('IfcConversionBasedUnit') and not unit.is_a('IfcConversionBasedUnitWithOffset'):
        dimensions = unit.Dimensions
        if (dimensions is None or not hasattr(dimensions, 'source_attribute')
                or not dimensions.is_a('IfcDimensionalExponents') or len(dimensions) != 7):
            raise ValueError('Exact conversion unit dimensions unavailable')
        exponents = [dimensions.source_attribute(i) for i in range(7)]
        if any(type(x) is not int for x in exponents) or tuple(exponents) != (power, 0, 0, 0, 0, 0, 0):
            raise ValueError('Exact conversion unit dimensions conflict')
        conversion = unit.ConversionFactor
        component = conversion.source_attribute('ValueComponent')
        if not isinstance(component, dict) or set(component) != {'type', 'value'}:
            raise ValueError('Exact conversion factor source wrapper unavailable')
        kind_name = conversion.ValueComponent.is_a()
        if kind_name not in ('IfcReal', 'IfcRatioMeasure', 'IfcPositiveRatioMeasure') and MEASURES.get(kind_name) != kind:
            raise ValueError('Exact conversion factor measure type conflicts')
        factor = _source_decimal(component['value'])
        if factor <= 0:
            raise ValueError('Invalid exact conversion factor')
        return _exact_product(factor, unit_scale_exact(conversion.UnitComponent, kind, visited | {unit.id()}))
    raise ValueError('Unsupported exact unit form')


def exact_measure(model, row, unit, kind):
    """Additive text contract: source path, exact decimal SI and approximation flag."""
    result = {'source_real_lexeme': None, 'exact_scale_to_si': None, 'exact_si_value': None,
              'exact_status': 'UNRESOLVED_EXACT', 'exact_reason': '',
              'numeric_precision': 'UNQUALIFIED'}
    try:
        entity = model.by_id(int(row['property_step_id']))
        attribute = QUANTITIES[row['ifc_class']][1] if row['ifc_class'] in QUANTITIES else 'NominalValue'
        node = entity.source_attribute(attribute)
        if attribute == 'NominalValue':
            if not isinstance(node, dict) or set(node) != {'type', 'value'}:
                raise ValueError('Exact nominal source wrapper unavailable')
            node = node['value']
        if isinstance(node, dict):
            result['source_real_lexeme'] = node.get('step_real')
        exact = _source_decimal(node)
        factor = unit_scale_exact(unit, kind)
        normalized = _exact_product(exact, factor)
        result.update(exact_scale_to_si=str(factor), exact_si_value=str(normalized),
                      exact_status='EXACT_DECLARED_DECIMAL_SI')
    except (ValueError, TypeError, AttributeError, KeyError, ArithmeticError) as error:
        result['exact_reason'] = str(error)
    return result


def unit_scale(unit, kind, visited=frozenset()):
    if unit is None or unit.id() in visited or getattr(unit, "UnitType", None) != kind:
        raise ValueError("Missing, cyclic or dimensionally incompatible unit")
    # Match the exact arithmetic budget: at most32 unit nodes, including SI.
    if len(visited) >= MAX_EXACT_UNIT_DEPTH:
        raise ValueError("Approximate unit conversion exceeds the 32-unit depth limit")
    expected, power, _ = KINDS[kind]
    if unit.is_a("IfcSIUnit"):
        if unit.Name != expected or unit.Prefix not in PREFIX:
            raise ValueError("Unsupported SI declaration")
        return PREFIX[unit.Prefix] ** power
    if unit.is_a("IfcConversionBasedUnit") and not unit.is_a("IfcConversionBasedUnitWithOffset"):
        dims = unit.Dimensions
        # Validate the source integer exponents, not model floats/bools which
        # can compare equal to integers after rounding or logical conversion.
        if (dims is None or not hasattr(dims, "source_attribute")
                or not dims.is_a("IfcDimensionalExponents") or len(dims) != 7):
            raise ValueError("Conversion unit dimensions unavailable")
        exponents = [dims.source_attribute(i) for i in range(7)]
        if any(type(x) is not int for x in exponents) or tuple(exponents) != (power, 0, 0, 0, 0, 0, 0):
            raise ValueError("Conversion unit dimensions conflict")
        conversion = unit.ConversionFactor
        factor_type = conversion.ValueComponent.is_a()
        if factor_type not in ("IfcReal", "IfcRatioMeasure", "IfcPositiveRatioMeasure") and MEASURES.get(factor_type) != kind:
            raise ValueError("Conversion factor measure type conflicts with unit dimension")
        factor = conversion.ValueComponent.wrappedValue
        if isinstance(factor, bool) or not isinstance(factor, (int, float)) or not math.isfinite(factor) or factor <= 0:
            raise ValueError("Invalid conversion factor")
        scale = factor * unit_scale(conversion.UnitComponent, kind, visited | {unit.id()})
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("Conversion scale overflow or underflow")
        return scale
    raise ValueError("Unsupported unit form")


def records(tables, name):
    # Keyset batches finish each cursor before downstream writes. Do not retain
    # the project's complete decoded property graph alongside the IFC model.
    last = 0
    while True:
        cursor = tables.db.execute(
            "SELECT ordinal,record_json FROM records WHERE table_name=? AND ordinal>? ORDER BY ordinal LIMIT 256",
            (name, last))
        try:
            batch = cursor.fetchall()
        finally:
            cursor.close()
        if not batch:
            return
        for ordinal, raw in batch:
            yield json.loads(raw)
            last = ordinal


def owner_groups(tables):
    """One owner's candidate graph at a time; IDs/ordinals live in SQLite."""
    db = tables.db
    db.execute("CREATE TEMP TABLE ddc_semantic_owners(table_name TEXT, owner TEXT, scope TEXT, ordinal INTEGER, PRIMARY KEY(table_name,owner,scope,ordinal)) WITHOUT ROWID")
    try:
        db.execute("INSERT INTO ddc_semantic_owners SELECT table_name,json_extract(record_json,'$.owner_step_id'),coalesce(json_extract(record_json,'$.scope'),''),ordinal FROM records WHERE table_name IN ('Properties','TypeLinks')")
        owners = [r[0] for r in db.execute("SELECT DISTINCT owner FROM ddc_semantic_owners WHERE table_name='TypeLinks' OR (table_name='Properties' AND scope<>'TYPE_DEFINITION') ORDER BY owner").fetchall()]

        def rows(table, owner, type_definition=False):
            op = '=' if type_definition else '<>'
            query = ("SELECT r.record_json FROM ddc_semantic_owners i JOIN records r ON r.table_name=i.table_name AND r.ordinal=i.ordinal "
                     "WHERE i.table_name=? AND i.owner=? AND i.scope " + op + " 'TYPE_DEFINITION' ORDER BY i.ordinal")
            return [json.loads(r[0]) for r in db.execute(query, (table, owner)).fetchall()]

        for owner in owners:
            direct = rows('Properties', owner)
            links = rows('TypeLinks', owner)
            inherited = []
            for link in links:
                # Repeated type relations retain repeated candidates.
                inherited.extend(rows('Properties', link['type_step_id'], True))
            yield owner, direct, links, inherited
    finally:
        db.execute("DROP TABLE ddc_semantic_owners")


def derive(model, tables):
    statuses = Counter()
    with closing(owner_groups(tables)) as owners:
        for owner, direct, links, inherited_rows in owners:
            groups = defaultdict(lambda: {"occurrence": [], "type": []})
            named_sets = defaultdict(set)
            for row in direct:
                groups[tuple(row["path"])]["occurrence"].append(row)
                named_sets[("occurrence", row["path"][0])].add(row["root_set_step_id"])
            for row in inherited_rows:
                groups[tuple(row["path"])]["type"].append(row)
                named_sets[("type", row["path"][0])].add(row["root_set_step_id"])
            for path, candidates in groups.items():
                occurrence, inherited = candidates["occurrence"], candidates["type"]
                ambiguous = (len(occurrence) > 1 or len(inherited) > 1 or len(links) > 1
                             or any(p is None for p in path)
                             or any(len(named_sets[(scope, path[0])]) > 1 for scope in ("occurrence", "type"))
                             or len(path) != 2
                             or any(r["status"] != "SOURCE_VALUE" for r in occurrence + inherited))
                selected = None if ambiguous else (occurrence or inherited)[0]
                status = "AMBIGUOUS_NOT_RESOLVED" if ambiguous else ("OCCURRENCE_OVERRIDES_TYPE" if occurrence and inherited else "OCCURRENCE_ONLY" if occurrence else "INHERITED_TYPE")
                statuses[status] += 1
                tables.emit("EffectiveProperties", {"owner_step_id": owner, "path": list(path), "status": status,
                            "selected_property_step_id": selected["property_step_id"] if selected else None,
                            "selected_scope": selected["scope"] if selected else None,
                            "value": selected["value"] if selected else None,
                            "source_real_values": selected.get("source_real_values", []) if selected else [],
                            "unit_step_id": selected["unit_step_id"] if selected else None,
                            "occurrence_candidates": occurrence, "type_candidates": inherited,
                            "type_relations": links})
    projects = model.by_type("IfcProject")
    project_units = list(projects[0].UnitsInContext.Units or ()) if len(projects) == 1 and projects[0].UnitsInContext else []
    unit_statuses = Counter()
    for row in chain(records(tables, "Properties"), records(tables, "Quantities")):
        kind, number = None, None
        attrs = row["attributes"]
        if row["ifc_class"] in QUANTITIES:
            kind, attribute = QUANTITIES[row["ifc_class"]]
            number = attrs.get(attribute)
        elif row["ifc_class"] == "IfcPropertySingleValue":
            wrapped = attrs.get("NominalValue") or {}
            kind, number = MEASURES.get(wrapped.get("ifc_type")), wrapped.get("value")
        if kind is None:
            continue
        unit = model.by_id(int(row["unit_step_id"])) if row["unit_step_id"] else None
        origin = "EXPLICIT" if unit else "PROJECT_DEFAULT"
        if unit is None:
            matches = [u for u in project_units if getattr(u, "UnitType", None) == kind]
            unit = matches[0] if len(matches) == 1 else None
        status, factor, normalized, reason = "UNRESOLVED_UNIT", None, None, ""
        try:
            if isinstance(number, bool) or not isinstance(number, (float, int)) or not math.isfinite(number):
                raise ValueError("Non-finite or non-numeric measure")
            factor = unit_scale(unit, kind)
            # An identity conversion must not round a source integer through
            # binary64 (e.g. 9007199254740993 * 1.0 loses one source unit).
            normalized = number if factor == 1 else number * factor
            if not math.isfinite(normalized):
                raise ValueError("Normalized measure overflow")
            if number != 0 and normalized == 0:
                raise ValueError("Normalized measure underflow")
            status = "NORMALIZED_SI"
        except (ValueError, TypeError, AttributeError) as exc:
            factor, normalized, reason = None, None, str(exc)
        unit_statuses[status] += 1
        precision = exact_measure(model, row, unit, kind)
        if precision['exact_status'] == 'EXACT_DECLARED_DECIMAL_SI' and normalized is not None:
            numeric = Decimal(normalized) if type(normalized) is int else Decimal.from_float(normalized)
            target = Decimal(precision['exact_si_value'])
            precision['numeric_precision'] = ('EXACT_NUMERIC' if numeric == target and numeric.is_signed() == target.is_signed()
                                              else 'APPROXIMATE_NUMERIC_USE_EXACT_TEXT')
        tables.emit("NormalizedMeasures", {"owner_step_id": row["owner_step_id"], "scope": row["scope"],
                    "property_step_id": row["property_step_id"], "path": row["path"], "raw_value": number,
                    "raw_unit_step_id": row["unit_step_id"], "resolved_unit_step_id": str(unit.id()) if unit else None,
                    "unit_origin": origin, "unit_kind": kind, "scale_to_si": factor,
                    "si_value": normalized, "si_unit": KINDS[kind][2], "status": status, "reason": reason,
                    **precision,
                    "relation_step_id": row["relation_step_id"], "root_set_step_id": row["root_set_step_id"],
                    "set_step_id": row["set_step_id"]})
    return {"effective_property_statuses": dict(statuses), "normalized_measure_statuses": dict(unit_statuses)}
