"""Schema-free IFC model: generic positional STEP reader + a small hand-written core table.

Simplified mode for IFC to Excel and DDC Viewer (owner decision 2026-10-16): no
data generated from the buildingSMART EXPRESS schemas is shipped or loaded.

* The parser reads ISO 10303-21 (STEP physical file) syntax only: every entity
  instance becomes its type name exactly as written in the file plus its raw,
  positional attribute list.  Nothing is validated against a schema and no
  attribute is ever filled in by default.
* ``CORE`` below is our own table, written by hand from publicly known IFC class
  and attribute names, for the entities we interpret (spatial tree, names,
  property sets, quantities, materials, units, styles, placements, geometry).
  It holds only display spellings and attribute names in positional order; no
  schema text, no WHERE rules, no generated inheritance graph.
* ``FAMILY`` rules answer the few supertype questions our code asks (e.g. "is
  this a relationship?") from the file itself (name patterns, attribute shapes)
  plus short hand-written lists.
* Every other entity is exposed generically: its file spelling as type name,
  attribute names ``Attr1..AttrN``.

API subset compatible with ``model.py``: ``model_from_file``, ``Model.iter /
by_id / by_type / schema``, ``Entity.id / is_a / attribute_name / len / [] /
attribute access / source_attribute / source_real_values``, ``TypedValue``.
"""
from __future__ import annotations

import math
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODE = 'SCHEMA_FREE_CORE_TABLE'


class ModelError(ValueError):
    pass


# ----------------------------------------------------------------------------- own core table
_ROOT = 'GlobalId OwnerHistory Name Description'
_OBJECT = _ROOT + ' ObjectType'
_PRODUCT = _OBJECT + ' ObjectPlacement Representation'
_ELEMENT = _PRODUCT + ' Tag'
_SPATIAL = _PRODUCT + ' LongName CompositionType'
_TYPE = _ROOT + ' ApplicableOccurrence HasPropertySets'
_REL = _ROOT
_PROFILE = 'ProfileType ProfileName'
_QUANTITY = 'Name Description Unit'

CORE = {
    # spatial structure and objects
    'IfcProject': _OBJECT + ' LongName Phase RepresentationContexts UnitsInContext',
    'IfcSite': _SPATIAL + ' RefLatitude RefLongitude RefElevation LandTitleNumber SiteAddress',
    'IfcBuilding': _SPATIAL + ' ElevationOfRefHeight ElevationOfTerrain BuildingAddress',
    'IfcBuildingStorey': _SPATIAL + ' Elevation',
    'IfcSpace': _SPATIAL,
    'IfcOpeningElement': _ELEMENT,
    # relationships
    'IfcRelAggregates': _REL + ' RelatingObject RelatedObjects',
    'IfcRelNests': _REL + ' RelatingObject RelatedObjects',
    'IfcRelContainedInSpatialStructure': _REL + ' RelatedElements RelatingStructure',
    'IfcRelReferencedInSpatialStructure': _REL + ' RelatedElements RelatingStructure',
    'IfcRelDefinesByProperties': _REL + ' RelatedObjects RelatingPropertyDefinition',
    'IfcRelDefinesByType': _REL + ' RelatedObjects RelatingType',
    'IfcRelAssociatesMaterial': _REL + ' RelatedObjects RelatingMaterial',
    'IfcRelVoidsElement': _REL + ' RelatingBuildingElement RelatedOpeningElement',
    'IfcRelFillsElement': _REL + ' RelatingOpeningElement RelatedBuildingElement',
    # properties and quantities
    'IfcPropertySet': _ROOT + ' HasProperties',
    'IfcElementQuantity': _ROOT + ' MethodOfMeasurement Quantities',
    'IfcPropertySingleValue': 'Name Description NominalValue Unit',
    'IfcPropertyEnumeratedValue': 'Name Description EnumerationValues EnumerationReference',
    'IfcPropertyListValue': 'Name Description ListValues Unit',
    'IfcComplexProperty': 'Name Description UsageName HasProperties',
    'IfcPhysicalComplexQuantity': 'Name Description HasQuantities Discrimination Quality Usage',
    'IfcPropertyReferenceValue': 'Name Description UsageName PropertyReference',
    'IfcPropertyTableValue': 'Name Description DefiningValues DefinedValues Expression DefiningUnit DefinedUnit CurveInterpolation',
    'IfcQuantityLength': _QUANTITY + ' LengthValue Formula',
    'IfcQuantityArea': _QUANTITY + ' AreaValue Formula',
    'IfcQuantityVolume': _QUANTITY + ' VolumeValue Formula',
    'IfcQuantityCount': _QUANTITY + ' CountValue Formula',
    'IfcQuantityWeight': _QUANTITY + ' WeightValue Formula',
    'IfcQuantityTime': _QUANTITY + ' TimeValue Formula',
    # materials
    'IfcMaterial': 'Name Description Category',
    'IfcMaterialList': 'Materials',
    'IfcMaterialLayer': 'Material LayerThickness IsVentilated Name Description Category Priority',
    'IfcMaterialLayerSet': 'MaterialLayers LayerSetName Description',
    'IfcMaterialLayerSetUsage': 'ForLayerSet LayerSetDirection DirectionSense OffsetFromReferenceLine ReferenceExtent',
    'IfcMaterialConstituent': 'Name Description Material Fraction Category',
    'IfcMaterialConstituentSet': 'Name Description MaterialConstituents',
    'IfcMaterialProfile': 'Name Description Material Profile Priority Category',
    'IfcMaterialProfileSet': 'Name Description MaterialProfiles CompositeProfile',
    'IfcMaterialProfileSetUsage': 'ForProfileSet CardinalPoint ReferenceExtent',
    'IfcMaterialDefinitionRepresentation': 'Name Description Representations RepresentedMaterial',
    # units
    'IfcUnitAssignment': 'Units',
    'IfcSIUnit': 'Dimensions UnitType Prefix Name',
    'IfcConversionBasedUnit': 'Dimensions UnitType Name ConversionFactor',
    'IfcConversionBasedUnitWithOffset': 'Dimensions UnitType Name ConversionFactor ConversionOffset',
    'IfcContextDependentUnit': 'Dimensions UnitType Name',
    'IfcMeasureWithUnit': 'ValueComponent UnitComponent',
    'IfcDimensionalExponents': 'LengthExponent MassExponent TimeExponent ElectricCurrentExponent '
                               'ThermodynamicTemperatureExponent AmountOfSubstanceExponent LuminousIntensityExponent',
    # presentation
    'IfcStyledItem': 'Item Styles Name',
    'IfcStyledRepresentation': 'ContextOfItems RepresentationIdentifier RepresentationType Items',
    'IfcPresentationStyleAssignment': 'Styles',
    'IfcSurfaceStyle': 'Name Side Styles',
    'IfcSurfaceStyleShading': 'SurfaceColour Transparency',
    'IfcSurfaceStyleRendering': 'SurfaceColour Transparency DiffuseColour TransmissionColour DiffuseTransmissionColour '
                                'ReflectionColour SpecularColour SpecularHighlight ReflectanceMethod',
    'IfcColourRgb': 'Name Red Green Blue',
    # placement and representation
    'IfcLocalPlacement': 'PlacementRelTo RelativePlacement',
    'IfcAxis2Placement3D': 'Location Axis RefDirection',
    'IfcAxis2Placement2D': 'Location RefDirection',
    'IfcCartesianPoint': 'Coordinates',
    'IfcDirection': 'DirectionRatios',
    'IfcVector': 'Orientation Magnitude',
    'IfcProductDefinitionShape': 'Name Description Representations',
    'IfcShapeRepresentation': 'ContextOfItems RepresentationIdentifier RepresentationType Items',
    'IfcTopologyRepresentation': 'ContextOfItems RepresentationIdentifier RepresentationType Items',
    'IfcGeometricRepresentationContext': 'ContextIdentifier ContextType CoordinateSpaceDimension Precision '
                                         'WorldCoordinateSystem TrueNorth',
    'IfcRepresentationMap': 'MappingOrigin MappedRepresentation',
    'IfcMappedItem': 'MappingSource MappingTarget',
    'IfcCartesianTransformationOperator3D': 'Axis1 Axis2 LocalOrigin Scale Axis3',
    'IfcCartesianTransformationOperator3DnonUniform': 'Axis1 Axis2 LocalOrigin Scale Axis3 Scale2 Scale3',
    # geometry items
    'IfcCartesianPointList3D': 'CoordList TagList',
    'IfcCartesianPointList2D': 'CoordList TagList',
    'IfcTriangulatedFaceSet': 'Coordinates Normals Closed CoordIndex PnIndex',
    'IfcTriangulatedIrregularNetwork': 'Coordinates Normals Closed CoordIndex PnIndex Flags',
    'IfcPolygonalFaceSet': 'Coordinates Closed Faces PnIndex',
    'IfcIndexedPolygonalFace': 'CoordIndex',
    'IfcIndexedPolygonalFaceWithVoids': 'CoordIndex InnerCoordIndices',
    'IfcFacetedBrep': 'Outer',
    'IfcFacetedBrepWithVoids': 'Outer Voids',
    'IfcClosedShell': 'CfsFaces',
    'IfcOpenShell': 'CfsFaces',
    'IfcConnectedFaceSet': 'CfsFaces',
    'IfcFace': 'Bounds',
    'IfcFaceBound': 'Bound Orientation',
    'IfcFaceOuterBound': 'Bound Orientation',
    'IfcPolyLoop': 'Polygon',
    'IfcShellBasedSurfaceModel': 'SbsmBoundary',
    'IfcFaceBasedSurfaceModel': 'FbsmFaces',
    'IfcBooleanResult': 'Operator FirstOperand SecondOperand',
    'IfcBooleanClippingResult': 'Operator FirstOperand SecondOperand',
    'IfcExtrudedAreaSolid': 'SweptArea Position ExtrudedDirection Depth',
    'IfcHalfSpaceSolid': 'BaseSurface AgreementFlag',
    'IfcBoxedHalfSpace': 'BaseSurface AgreementFlag Enclosure',
    'IfcPolygonalBoundedHalfSpace': 'BaseSurface AgreementFlag Position PolygonalBoundary',
    'IfcPlane': 'Position',
    'IfcRectangleProfileDef': _PROFILE + ' Position XDim YDim',
    'IfcRoundedRectangleProfileDef': _PROFILE + ' Position XDim YDim RoundingRadius',
    'IfcRectangleHollowProfileDef': _PROFILE + ' Position XDim YDim WallThickness InnerFilletRadius OuterFilletRadius',
    'IfcCircleProfileDef': _PROFILE + ' Position Radius',
    'IfcCircleHollowProfileDef': _PROFILE + ' Position Radius WallThickness',
    'IfcEllipseProfileDef': _PROFILE + ' Position SemiAxis1 SemiAxis2',
    'IfcArbitraryClosedProfileDef': _PROFILE + ' OuterCurve',
    'IfcIShapeProfileDef': _PROFILE + ' Position OverallWidth OverallDepth WebThickness FlangeThickness FilletRadius',
    'IfcLShapeProfileDef': _PROFILE + ' Position Depth Width Thickness FilletRadius EdgeRadius',
    'IfcTShapeProfileDef': _PROFILE + ' Position Depth FlangeWidth WebThickness FlangeThickness FilletRadius',
    'IfcUShapeProfileDef': _PROFILE + ' Position Depth FlangeWidth WebThickness FlangeThickness FilletRadius',
    'IfcCShapeProfileDef': _PROFILE + ' Position Depth Width WallThickness Girth InternalFilletRadius',
    'IfcZShapeProfileDef': _PROFILE + ' Position Depth FlangeWidth WebThickness FlangeThickness FilletRadius',
    'IfcArbitraryProfileDefWithVoids': _PROFILE + ' OuterCurve InnerCurves',
    'IfcPolyline': 'Points',
    'IfcIndexedPolyCurve': 'Points Segments SelfIntersect',
    'IfcCircle': 'Position Radius',
    'IfcEllipse': 'Position SemiAxis1 SemiAxis2',
    'IfcLine': 'Pnt Dir',
    'IfcTrimmedCurve': 'BasisCurve Trim1 Trim2 SenseAgreement MasterRepresentation',
    'IfcCompositeCurve': 'Segments SelfIntersect',
    'IfcCompositeCurveSegment': 'Transition SameSense ParentCurve',
    # advanced boundary representation (IFC4) and further solids
    'IfcAdvancedBrep': 'Outer',
    'IfcAdvancedBrepWithVoids': 'Outer Voids',
    'IfcFaceSurface': 'Bounds FaceSurface SameSense',
    'IfcAdvancedFace': 'Bounds FaceSurface SameSense',
    'IfcEdgeLoop': 'EdgeList',
    'IfcOrientedEdge': 'EdgeStart EdgeEnd EdgeElement Orientation',
    'IfcEdgeCurve': 'EdgeStart EdgeEnd EdgeGeometry SameSense',
    'IfcEdge': 'EdgeStart EdgeEnd',
    'IfcVertexPoint': 'VertexGeometry',
    'IfcAxis1Placement': 'Location Axis',
    'IfcCylindricalSurface': 'Position Radius',
    'IfcConicalSurface': 'Position Radius SemiAngle',
    'IfcSphericalSurface': 'Position Radius',
    'IfcToroidalSurface': 'Position MajorRadius MinorRadius',
    'IfcSurfaceOfRevolution': 'SweptCurve Position AxisPosition',
    'IfcSurfaceOfLinearExtrusion': 'SweptCurve Position ExtrudedDirection Depth',
    'IfcArbitraryOpenProfileDef': _PROFILE + ' Curve',
    'IfcBSplineCurveWithKnots': 'Degree ControlPointsList CurveForm ClosedCurve SelfIntersect '
                                'KnotMultiplicities Knots KnotSpec',
    'IfcRationalBSplineCurveWithKnots': 'Degree ControlPointsList CurveForm ClosedCurve SelfIntersect '
                                        'KnotMultiplicities Knots KnotSpec WeightsData',
    'IfcBSplineSurfaceWithKnots': 'UDegree VDegree ControlPointsList SurfaceForm UClosed VClosed SelfIntersect '
                                  'UMultiplicities VMultiplicities UKnots VKnots KnotSpec',
    'IfcRationalBSplineSurfaceWithKnots': 'UDegree VDegree ControlPointsList SurfaceForm UClosed VClosed '
                                          'SelfIntersect UMultiplicities VMultiplicities UKnots VKnots KnotSpec '
                                          'WeightsData',
    'IfcRevolvedAreaSolid': 'SweptArea Position Axis Angle',
}
CORE = {name: tuple(attrs.split()) for name, attrs in CORE.items()}
SPELLING = {name.upper(): name for name in CORE}
# IFC4 bounded value order (upper first); hand-written for both releases we read.
CORE['IfcPropertyBoundedValue'] = ('Name', 'Description', 'UpperBoundValue', 'LowerBoundValue', 'Unit', 'SetPointValue')
SPELLING['IFCPROPERTYBOUNDEDVALUE'] = 'IfcPropertyBoundedValue'

# Display spellings of common element / type classes (names only; their attributes come from the
# product / type layout rules below).  Unlisted classes keep the spelling found in the file.
DISPLAY_ONLY = '''IfcWall IfcWallStandardCase IfcCurtainWall IfcSlab IfcRoof IfcBeam IfcColumn IfcMember IfcPlate IfcWindow
IfcDoor IfcStair IfcStairFlight IfcRamp IfcRampFlight IfcRailing IfcFooting IfcPile IfcCovering IfcChimney
IfcShadingDevice IfcBuildingElementProxy IfcBuildingElementPart IfcElementAssembly IfcFurnishingElement
IfcFurniture IfcSystemFurnitureElement IfcFlowSegment IfcFlowFitting IfcFlowTerminal IfcFlowController
IfcFlowMovingDevice IfcFlowStorageDevice IfcFlowTreatmentDevice IfcEnergyConversionDevice IfcDistributionElement
IfcDistributionControlElement IfcDistributionFlowElement IfcDistributionPort IfcPipeSegment IfcPipeFitting
IfcDuctSegment IfcDuctFitting IfcCableSegment IfcCableCarrierSegment IfcAirTerminal IfcLightFixture
IfcSanitaryTerminal IfcFireSuppressionTerminal IfcAlarm IfcCommunicationsAppliance IfcDistributionChamberElement
IfcTransportElement IfcVirtualElement IfcGeographicElement IfcAnnotation IfcGrid IfcGridAxis IfcProxy
IfcReinforcingBar IfcReinforcingMesh IfcTendon IfcDiscreteAccessory IfcFastener IfcMechanicalFastener
IfcCivilElement IfcElementComponent IfcFeatureElement IfcProjectionElement IfcSpatialZone IfcZone
IfcWallType IfcSlabType IfcBeamType IfcColumnType IfcMemberType IfcPlateType IfcWindowType IfcDoorType
IfcWindowStyle IfcDoorStyle IfcCoveringType IfcRailingType IfcStairFlightType IfcFurnitureType
IfcBuildingElementProxyType IfcFootingType IfcPileType IfcRoofType IfcCurtainWallType IfcSpaceType'''.split()
for _name in DISPLAY_ONLY:
    SPELLING.setdefault(_name.upper(), _name)

# Display spellings of common defined (value) types, e.g. IFCLENGTHMEASURE('2.') -> IfcLengthMeasure.
TYPE_SPELLING = {n.upper(): n for n in '''IfcLengthMeasure IfcPositiveLengthMeasure IfcNonNegativeLengthMeasure
IfcAreaMeasure IfcVolumeMeasure IfcLabel IfcText IfcIdentifier IfcBoolean IfcLogical IfcInteger IfcReal
IfcPositiveInteger IfcCountMeasure IfcMassMeasure IfcPlaneAngleMeasure IfcPositivePlaneAngleMeasure
IfcRatioMeasure IfcPositiveRatioMeasure IfcNormalisedRatioMeasure IfcThermalTransmittanceMeasure IfcPowerMeasure
IfcTimeMeasure IfcParameterValue IfcElectricCurrentMeasure IfcElectricVoltageMeasure IfcFrequencyMeasure
IfcPressureMeasure IfcForceMeasure IfcMonetaryMeasure IfcDate IfcDateTime IfcTime IfcDuration
IfcLuminousFluxMeasure IfcIlluminanceMeasure IfcThermodynamicTemperatureMeasure IfcVolumetricFlowRateMeasure
IfcMassDensityMeasure IfcDescriptiveMeasure IfcURIReference IfcNumericMeasure IfcContextDependentMeasure
IfcPropertySetDefinitionSet IfcLineIndex IfcArcIndex'''.split()}

# Hand-written "is also a" answers our code needs (child -> parents).
PARENTS = {
    'IFCFACEOUTERBOUND': ('IfcFaceBound',),
    'IFCFACETEDBREPWITHVOIDS': ('IfcFacetedBrep',),
    'IFCSURFACESTYLERENDERING': ('IfcSurfaceStyleShading',),
    'IFCBOOLEANCLIPPINGRESULT': ('IfcBooleanResult',),
    'IFCBOXEDHALFSPACE': ('IfcHalfSpaceSolid',),
    'IFCPOLYGONALBOUNDEDHALFSPACE': ('IfcHalfSpaceSolid',),
    'IFCINDEXEDPOLYGONALFACEWITHVOIDS': ('IfcIndexedPolygonalFace',),
    'IFCCONVERSIONBASEDUNITWITHOFFSET': ('IfcConversionBasedUnit',),
    'IFCCARTESIANTRANSFORMATIONOPERATOR3DNONUNIFORM': ('IfcCartesianTransformationOperator3D',),
    'IFCRECTANGLEHOLLOWPROFILEDEF': ('IfcRectangleProfileDef',),
    'IFCROUNDEDRECTANGLEPROFILEDEF': ('IfcRectangleProfileDef',),
    'IFCCIRCLEHOLLOWPROFILEDEF': ('IfcCircleProfileDef',),
    'IFCARBITRARYPROFILEDEFWITHVOIDS': ('IfcArbitraryClosedProfileDef',),
    'IFCTRIANGULATEDIRREGULARNETWORK': ('IfcTriangulatedFaceSet',),
    'IFCADVANCEDBREPWITHVOIDS': ('IfcAdvancedBrep',),
    'IFCADVANCEDFACE': ('IfcFaceSurface', 'IfcFace'),
    'IFCFACESURFACE': ('IfcFace',),
    'IFCRATIONALBSPLINECURVEWITHKNOTS': ('IfcBSplineCurveWithKnots',),
    'IFCRATIONALBSPLINESURFACEWITHKNOTS': ('IfcBSplineSurfaceWithKnots',),
}
NAMED_UNITS = {'IFCSIUNIT', 'IFCCONVERSIONBASEDUNIT', 'IFCCONVERSIONBASEDUNITWITHOFFSET', 'IFCCONTEXTDEPENDENTUNIT'}
PROPERTY_DEFINITIONS = {'IFCPROPERTYSET', 'IFCELEMENTQUANTITY', 'IFCPROPERTYSETTEMPLATE'}
PLACEMENTS = {'IFCLOCALPLACEMENT', 'IFCGRIDPLACEMENT', 'IFCLINEARPLACEMENT'}
SHAPES = {'IFCPRODUCTDEFINITIONSHAPE', 'IFCMATERIALDEFINITIONREPRESENTATION'}


# ----------------------------------------------------------------------------- STEP parser
class _Text:
    def __init__(self, text):
        self.t = text
        self.i = 0
        self.n = len(text)

    def skip(self):
        t, n = self.t, self.n
        while self.i < n:
            c = t[self.i]
            if c in ' \t\r\n':
                self.i += 1
            elif c == '/' and t.startswith('/*', self.i):
                end = t.find('*/', self.i + 2)
                if end < 0:
                    raise ModelError('Unterminated comment')
                self.i = end + 2
            else:
                return

    def peek(self):
        self.skip()
        return self.t[self.i] if self.i < self.n else ''

    def expect(self, c):
        if self.peek() != c:
            raise ModelError('Expected %r at offset %d' % (c, self.i))
        self.i += 1


def _decode_string(raw):
    """STEP string escapes: '' quote, \\\\ backslash, \\S\\c, \\X\\hh, \\X2\\...\\X0\\, \\X4\\...\\X0\\; \\P?\\ ignored."""
    out = []
    i, n = 0, len(raw)
    while i < n:
        c = raw[i]
        if c == "'" and i + 1 < n and raw[i + 1] == "'":
            out.append("'"); i += 2; continue
        if c != '\\':
            out.append(c); i += 1; continue
        if raw.startswith('\\\\', i):
            out.append('\\'); i += 2
        elif raw.startswith('\\S\\', i) and i + 3 < n:
            out.append(chr(ord(raw[i + 3]) + 128)); i += 4
        elif raw.startswith('\\X\\', i) and i + 5 <= n:
            out.append(chr(int(raw[i + 3:i + 5], 16))); i += 5
        elif raw.startswith('\\X2\\', i) or raw.startswith('\\X4\\', i):
            width = 4 if raw[i + 2] == '2' else 8
            end = raw.find('\\X0\\', i + 4)
            if end < 0:
                raise ModelError('Unterminated \\X2\\ / \\X4\\ string escape')
            hexes = raw[i + 4:end]
            for k in range(0, len(hexes), width):
                out.append(chr(int(hexes[k:k + width], 16)))
            i = end + 4
        elif raw.startswith('\\P', i) and i + 3 < n and raw[i + 3] == '\\':
            i += 4
        else:
            out.append(c); i += 1
    return ''.join(out)


def _number(token):
    if any(ch in token for ch in '.eE'):
        try:
            Decimal(token)
        except InvalidOperation as exc:
            raise ModelError('Bad real %r' % token) from exc
        return {'step_real': token}
    return int(token)


def _value(s):
    c = s.peek()
    t = s.t
    if c == '(':
        s.i += 1
        items = []
        if s.peek() == ')':
            s.i += 1
            return items
        while True:
            items.append(_value(s))
            c = s.peek()
            s.i += 1
            if c == ')':
                return items
            if c != ',':
                raise ModelError('Expected , or ) at offset %d' % (s.i - 1))
    if c == "'":
        j = s.i + 1
        while True:
            k = t.find("'", j)
            if k < 0:
                raise ModelError('Unterminated string')
            if k + 1 < s.n and t[k + 1] == "'":
                j = k + 2
                continue
            raw = t[s.i + 1:k]
            s.i = k + 1
            return _decode_string(raw)
    if c == '#':
        j = s.i + 1
        while j < s.n and t[j].isdigit():
            j += 1
        ref = int(t[s.i + 1:j])
        s.i = j
        return {'ref': ref}
    if c == '.':
        j = t.find('.', s.i + 1)
        token = t[s.i:j + 1]
        s.i = j + 1
        return {'enum': token}
    if c in '$*':
        s.i += 1
        return {'step_special': c}
    if c == '"':
        j = t.find('"', s.i + 1)
        token = t[s.i + 1:j]
        s.i = j + 1
        return {'binary': token}
    if c in '+-0123456789':
        j = s.i + 1
        while j < s.n and (t[j].isdigit() or t[j] in '.eE+-'):
            j += 1
        token = t[s.i:j]
        s.i = j
        return _number(token)
    if c.isalpha() or c == '_':
        j = s.i
        while j < s.n and (t[j].isalnum() or t[j] == '_'):
            j += 1
        name = t[s.i:j]
        s.i = j
        s.expect('(')
        inner = _value(s) if s.peek() != ')' else {'step_special': '$'}
        s.expect(')')
        return {'type': name, 'value': inner}
    raise ModelError('Unexpected character %r at offset %d' % (c, s.i))


def parse_text(text, cancel_event=None):
    """[{'id', 'type', 'attributes'}] of the DATA sections and the FILE_SCHEMA names."""
    s = _Text(text)
    schema_names = []
    head = text.find('FILE_SCHEMA')
    if head >= 0:
        s.i = head + len('FILE_SCHEMA')
        try:
            schema_names = [v for v in _flatten(_value(s)) if isinstance(v, str)]
        except ModelError:
            schema_names = []
    rows = []
    pos = 0
    while True:
        start = text.find('DATA', pos)
        if start < 0:
            break
        s.i = start + 4
        s.expect(';')
        while True:
            if cancel_event is not None and len(rows) % 4096 == 0 and cancel_event.is_set():
                raise ModelError('Cancelled during parsing')
            c = s.peek()
            if text.startswith('ENDSEC', s.i):
                s.i += 6
                s.expect(';')
                break
            if c != '#':
                raise ModelError('Expected entity instance at offset %d' % s.i)
            s.i += 1
            j = s.i
            while j < s.n and text[j].isdigit():
                j += 1
            ident = int(text[s.i:j])
            s.i = j
            s.expect('=')
            s.skip()
            j = s.i
            while j < s.n and (text[j].isalnum() or text[j] == '_'):
                j += 1
            name = text[s.i:j]
            s.i = j
            if not name:
                raise ModelError('Complex (multi-type) instances are not supported (#%d)' % ident)
            s.expect('(')
            attrs = [] if s.peek() == ')' else None
            if attrs is None:
                s.i -= 1
                attrs = _value(s)
            else:
                s.i += 1
            s.expect(';')
            rows.append({'id': ident, 'type': name, 'attributes': attrs})
        pos = s.i
    return rows, schema_names


def _flatten(v):
    if isinstance(v, list):
        for x in v:
            yield from _flatten(x)
    else:
        yield v


# ----------------------------------------------------------------------------- model
class TypedValue:
    """A defined-type wrapper as written in the file, e.g. IFCLABEL('x'); id is zero."""
    __slots__ = ('_type', 'wrappedValue')

    def __init__(self, type_name, wrapped):
        self._type = TYPE_SPELLING.get(type_name.upper(), type_name)
        self.wrappedValue = wrapped

    def id(self):
        return 0

    def is_a(self, type_name=None):
        if type_name is None:
            return self._type
        return self._type.casefold() == type_name.casefold()

    def __repr__(self):
        return '%s(%r)' % (self._type, self.wrappedValue)


class Entity:
    __slots__ = ('_model', '_id', '_upper', '_values', '_names')

    def __init__(self, model, ident, type_name, values):
        self._model = model
        self._id = ident
        self._upper = type_name.upper()
        self._values = values
        self._names = model._names_for(self._upper, values)

    def id(self):
        return self._id

    def is_a(self, type_name=None):
        own = SPELLING.get(self._upper, self._upper)
        if type_name is None:
            return own
        wanted = type_name.upper()
        if wanted == self._upper:
            return True
        if any(p.upper() == wanted for p in PARENTS.get(self._upper, ())):
            return True
        rule = FAMILY.get(wanted)
        return bool(rule and rule(self))

    def attribute_name(self, index):
        if not 0 <= index < len(self._values):
            raise IndexError(index)
        if index < len(self._names):
            return self._names[index]
        return 'Attr%d' % (index + 1)

    def __len__(self):
        return len(self._values)

    def __getitem__(self, index):
        return self._model._resolve(self._values[index])

    def __getattr__(self, name):
        try:
            index = self._names.index(name)
        except ValueError:
            raise AttributeError(name) from None
        if index >= len(self._values):
            raise AttributeError(name)
        return self[index]

    def source_attribute(self, attribute):
        if isinstance(attribute, str):
            try:
                attribute = self._names.index(attribute)
            except ValueError:
                raise AttributeError(attribute) from None
        return deepcopy(self._values[attribute])

    def source_real_values(self):
        output = []

        def walk(node, index, path, types):
            if isinstance(node, list):
                for position, child in enumerate(node):
                    walk(child, index, path + [position], types)
            elif isinstance(node, dict):
                if 'step_real' in node:
                    lexeme = node['step_real']
                    exact = Decimal(lexeme)
                    number = float(exact)
                    if not math.isfinite(number):
                        status = 'OVERFLOW_REFUSED'
                    elif number == 0 and exact != 0:
                        status = 'UNDERFLOW_REFUSED'
                    elif number != 0 and exact == exact.to_integral_value() and exact != Decimal.from_float(number):
                        status = 'EXACT_INTEGER'
                    else:
                        status = 'EXACT_BINARY64' if exact == Decimal.from_float(number) else 'ROUNDED_BINARY64'
                    output.append({'attribute_index': index, 'attribute_name': self.attribute_name(index),
                                   'value_path': path, 'defined_types': types, 'step_real': lexeme,
                                   'model_precision': status})
                elif 'type' in node:
                    walk(node['value'], index, path + ['value'], types + [node['type']])

        for index, node in enumerate(self._values):
            walk(node, index, [], [])
        return output

    def __repr__(self):
        return '#%d=%s' % (self._id, self._upper)


def _is_guid(v):
    return isinstance(v, str) and len(v) == 22


def _ref_type(model, node):
    if isinstance(node, dict) and 'ref' in node:
        target = model._rows.get(node['ref'])
        return target[0].upper() if target else None
    return None


def _product_like(model, upper, values):
    """IfcProduct layout recognised from the file: GlobalId, ..., placement ref or $, shape ref or $."""
    if len(values) < 7 or not _is_guid(values[0]) or upper.startswith('IFCREL') or _type_like(upper, values):
        return False
    p, r = values[5], values[6]
    ok_p = (isinstance(p, dict) and p.get('step_special') == '$') or _ref_type(model, p) in PLACEMENTS
    ok_r = (isinstance(r, dict) and r.get('step_special') == '$') or _ref_type(model, r) in SHAPES
    return ok_p and ok_r and (_ref_type(model, p) is not None or _ref_type(model, r) is not None or len(values) >= 8)


def _type_like(upper, values):
    return (upper.endswith(('TYPE', 'STYLE')) and len(values) >= 6 and _is_guid(values[0])
            and isinstance(values[5], (list, dict)))


class Model:
    def __init__(self, rows, schema, filename=None, cancel_event=None):
        self.schema = schema
        self.filename = filename
        self.mode = MODE
        self._rows = {r['id']: (r['type'], r['attributes']) for r in rows}
        self._entities = []
        self._by_id = {}
        for r in rows:
            if cancel_event is not None and cancel_event.is_set():
                raise ModelError('Cancelled during model construction')
            e = Entity(self, r['id'], r['type'], r['attributes'])
            self._entities.append(e)
            self._by_id[r['id']] = e

    def _names_for(self, upper, values):
        spelling = SPELLING.get(upper)
        if spelling in CORE:
            return CORE[spelling]
        if _type_like(upper, values):
            return tuple(_TYPE.split())
        if _product_like(self, upper, values):
            return CORE['IfcOpeningElement'] if len(values) >= 8 else CORE['IfcOpeningElement'][:7]
        if upper.startswith('IFCREL') and len(values) >= 4 and _is_guid(values[0]):
            return tuple(_REL.split())
        return ()

    def _resolve(self, node):
        if isinstance(node, list):
            return [self._resolve(x) for x in node]
        if not isinstance(node, dict):
            return node
        if 'ref' in node:
            try:
                return self._by_id[node['ref']]
            except KeyError:
                raise ModelError('Dangling reference #%d' % node['ref']) from None
        if 'step_special' in node:
            return None
        if 'enum' in node:
            enum = node['enum'].strip('.')
            return {'T': True, 'F': False, 'U': 'UNKNOWN'}.get(enum.upper(), enum)
        if 'step_real' in node:
            exact = Decimal(node['step_real'])
            number = float(exact)
            if not math.isfinite(number):
                raise ModelError('Non-finite real')
            if number == 0 and exact != 0:
                raise ModelError('STEP real underflows binary64; nonzero source value cannot be represented')
            if number != 0 and exact == exact.to_integral_value() and int(exact) != number:
                return int(exact)
            return number
        if 'type' in node:
            return TypedValue(node['type'], self._resolve(node['value']))
        if 'binary' in node:
            return node['binary']
        raise ModelError('Unsupported value node %r' % (node,))

    def __iter__(self):
        return iter(self._entities)

    def iter(self):
        return iter(self._entities)

    def by_id(self, ident):
        try:
            return self._by_id[int(ident)]
        except (KeyError, TypeError, ValueError) as exc:
            raise KeyError(ident) from exc

    def by_type(self, type_name, include_subtypes=True):
        if include_subtypes:
            return [e for e in self._entities if e.is_a(type_name)]
        wanted = type_name.upper()
        return [e for e in self._entities if e._upper == wanted]


FAMILY = {
    'IFCPRODUCT': lambda e: _product_like(e._model, e._upper, e._values),
    'IFCELEMENT': lambda e: _product_like(e._model, e._upper, e._values) and len(e._values) >= 8
    and e._upper not in ('IFCSITE', 'IFCBUILDING', 'IFCBUILDINGSTOREY', 'IFCSPACE'),
    'IFCSPATIALSTRUCTUREELEMENT': lambda e: e._upper in ('IFCSITE', 'IFCBUILDING', 'IFCBUILDINGSTOREY', 'IFCSPACE'),
    'IFCTYPEOBJECT': lambda e: _type_like(e._upper, e._values),
    'IFCRELATIONSHIP': lambda e: e._upper.startswith('IFCREL'),
    'IFCPROPERTYDEFINITION': lambda e: e._upper in PROPERTY_DEFINITIONS,
    'IFCPROPERTYSETDEFINITION': lambda e: e._upper in PROPERTY_DEFINITIONS,
    'IFCNAMEDUNIT': lambda e: e._upper in NAMED_UNITS,
    'IFCROOT': lambda e: len(e._values) >= 4 and _is_guid(e._values[0]),
    'IFCOBJECTDEFINITION': lambda e: (len(e._values) >= 4 and _is_guid(e._values[0]) and not e._upper.startswith('IFCREL')
                                      and e._upper not in PROPERTY_DEFINITIONS),
    'IFCPHYSICALQUANTITY': lambda e: e._upper.startswith('IFCQUANTITY'),
}


def model_from_file(path, schema_dir=None, *, cancel_event=None):
    """Parse an IFC-SPF file without any schema data; *schema_dir* is accepted and ignored."""
    source = Path(path)
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise ModelError('Cannot read IFC source %s: %s' % (source, exc)) from exc
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')     # STEP files are 7-bit with escapes; tolerate stray 8-bit bytes
    rows, names = parse_text(text, cancel_event=cancel_event)
    schema = (names[0].upper() if names else 'UNKNOWN')
    for prefix in ('IFC4X3', 'IFC4', 'IFC2X3'):
        if schema.startswith(prefix):
            schema = prefix
            break
    return Model(rows, schema, str(source), cancel_event=cancel_event)


def source_paths(schema=None):
    """Code paths only: this mode loads no schema data files."""
    return [HERE.joinpath('core_model.py').resolve()]


__all__ = ['Entity', 'Model', 'ModelError', 'TypedValue', 'model_from_file', 'source_paths', 'CORE', 'MODE']
