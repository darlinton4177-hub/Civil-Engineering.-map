# Seed catalog containing verified engineering domain entities
from typing import Dict, List

DEPARTMENTS: List[Dict] = [
    {
        "code": "civil",
        "name": "Civil & Environmental Engineering",
        "description": "Structural analysis, mechanics of materials, surveying geomatics, and transportation infrastructure.",
        "icon": "building-2",
    }
]

COURSES: List[Dict] = [
    {
        "department_code": "civil",
        "code": "CE-101",
        "title": "Statics & Strength of Materials",
        "level": "Undergraduate Year 1/2",
        "description": "Equilibrium of rigid bodies, axial stress/strain, torsion, and Mohr's stress circle transformation.",
        "order_index": 1,
    },
    {
        "department_code": "civil",
        "code": "CE-201",
        "title": "Structural Analysis I",
        "level": "Undergraduate Year 2",
        "description": "Determinate beams, shear force diagrams (SFD), bending moment diagrams (BMD), and elastic deflection.",
        "order_index": 2,
    },
    {
        "department_code": "civil",
        "code": "CE-202",
        "title": "Engineering Surveying & Geomatics",
        "level": "Undergraduate Year 2",
        "description": "Field measurement, differential leveling, Height of Instrument (HI) reduction, and arithmetic checks.",
        "order_index": 3,
    },
    {
        "department_code": "civil",
        "code": "CE-301",
        "title": "Highway Engineering & Geometric Design",
        "level": "Undergraduate Year 3",
        "description": "Equal-tangent vertical parabolic curves, sight distances, chainage profiles, and earthwork calculations.",
        "order_index": 4,
    },
    {
        "department_code": "civil",
        "code": "CE-302",
        "title": "Timber & Masonry Structural Design",
        "level": "Undergraduate Year 3",
        "description": "Code-based limit state checks for structural timber members in bending, horizontal shear, and serviceability deflection.",
        "order_index": 5,
    },
]

PROBLEM_MODULES: List[Dict] = [
    {
        "course_code": "CE-201",
        "slug": "simply-supported-beam",
        "title": "Simply Supported Beam: SFD & BMD",
        "description": "Calculate support reactions, shear force distribution, bending moment distribution, and maximum deflection for determinate single-span beams.",
        "discipline": "civil",
        "category": "structural",
        "status": "active",
        "version": "1.0.0",
        "icon": "activity",
    },
    {
        "course_code": "CE-101",
        "slug": "mohrs-circle",
        "title": "Mohr's Circle & Stress Transformation",
        "description": "Determine principal stresses, maximum in-plane shear stress, and orientation of principal planes for 2D plane stress states.",
        "discipline": "civil",
        "category": "materials",
        "status": "active",
        "version": "1.0.0",
        "icon": "compass",
    },
    {
        "course_code": "CE-202",
        "slug": "differential-leveling",
        "title": "Differential Leveling & Field Book Reduction",
        "description": "Calculate bench mark elevations using Height of Instrument (HI) and Rise & Fall methods with arithmetic closure checks.",
        "discipline": "civil",
        "category": "surveying",
        "status": "active",
        "version": "1.0.0",
        "icon": "map-pin",
    },
    {
        "course_code": "CE-301",
        "slug": "highway-vertical-curve",
        "title": "Highway Crest & Sag Vertical Curves",
        "description": "Calculate elevations along equal-tangent vertical parabolic curves, minimum curve length for stopping sight distance, and turning points.",
        "discipline": "civil",
        "category": "highway",
        "status": "active",
        "version": "1.0.0",
        "icon": "trending-up",
    },
    {
        "course_code": "CE-302",
        "slug": "timber-beam-check",
        "title": "Timber Member Bending & Shear Capacity",
        "description": "Standard-governed capacity checks for sawn timber beams against flexural stresses, horizontal shear, and live load deflections.",
        "discipline": "civil",
        "category": "timber",
        "status": "active",
        "version": "1.0.0",
        "icon": "shield",
    },
]
