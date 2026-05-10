from app.domain.evaluation.brand import score_brand
from app.domain.evaluation.category import score_category
from app.domain.evaluation.condition import score_condition
from app.domain.evaluation.design import score_design
from app.domain.evaluation.fit import score_fit
from app.domain.evaluation.hard_filters import HardFilterResult, apply_hard_filters
from app.domain.evaluation.hints import parse_design_hint, parse_make_hint, parse_material_hint
from app.domain.evaluation.make_quality import score_make_quality
from app.domain.evaluation.material import score_material
from app.domain.evaluation.price import score_price
from app.domain.evaluation.score import cheap_boost_material_domination, clamp_total
from app.domain.evaluation.verdict import surface_verdict_override, verdict_from_total

__all__ = [
    "HardFilterResult",
    "apply_hard_filters",
    "cheap_boost_material_domination",
    "clamp_total",
    "parse_design_hint",
    "parse_make_hint",
    "parse_material_hint",
    "score_brand",
    "score_category",
    "score_condition",
    "score_design",
    "score_fit",
    "score_make_quality",
    "score_material",
    "score_price",
    "surface_verdict_override",
    "verdict_from_total",
]
