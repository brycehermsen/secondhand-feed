from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from app.adapters.db.connection import connect, init_schema
from app.config.settings import Settings
from app.deps import build_deps
from app.domain.evaluation.pipeline import evaluate_eval_input, listing_and_eval_input_from_raw, listing_id_from_url
from app.domain.models.enums import Verdict
from app.domain.models.listing import RawListingSummary
from app.main import seed_sources


@pytest.fixture()
def profile_and_deps(tmp_path: Path):
    profile_src = Path(__file__).resolve().parents[3] / "data" / "buyer_style_profile.yaml"
    profile_dst = tmp_path / "buyer_style_profile.yaml"
    shutil.copyfile(profile_src, profile_dst)
    db = tmp_path / "t.db"
    settings = Settings.model_validate(
        {
            "DATABASE_PATH": str(db),
            "PROFILE_PATH": str(profile_dst),
            "FAKE_FIXTURE_PATH": str(tmp_path / "noop.json"),
        }
    )
    conn = connect(settings.database_path)
    init_schema(conn)
    deps = build_deps(conn, settings)
    seed_sources(deps)
    profile = deps.profile_store.load()
    return profile, profile_dst, deps


def _eval_fixture(profile, row: dict):
    raw = RawListingSummary.model_validate(
        {
            "marketplace": "fake",
            "canonical_url": row["url"],
            "title": row["title"],
            "brand_text": row.get("brand_text"),
            "price_text": row.get("price_text"),
            "shipping_text": row.get("shipping_text"),
            "image_url": row.get("image_url"),
            "condition_text": row.get("condition_text"),
            "size_text": row.get("size_text"),
            "category_hint": row.get("category_hint"),
            "description": row.get("description"),
            "design_level_hint": row.get("design_level_hint"),
            "make_quality_level_hint": row.get("make_quality_level_hint"),
            "material_level_hint": row.get("material_level_hint"),
            "measurements": row.get("measurements"),
        }
    )
    lid = listing_id_from_url(raw.canonical_url)
    inp = listing_and_eval_input_from_raw(raw, lid, profile)
    return evaluate_eval_input(inp, profile)


def test_plain_cashmere_overpriced_suppressed(profile_and_deps):
    profile, _, _ = profile_and_deps
    row = {
        "url": "fake://cashmere",
        "title": "Plain Cashmere Crewneck Sweater Size L",
        "brand_text": "Generic Luxury",
        "price_text": "$220",
        "shipping_text": "$15 shipping",
        "condition_text": "Very Good",
        "size_text": "L",
        "category_hint": "knitwear",
        "design_level_hint": "generic",
        "make_quality_level_hint": "ordinary",
        "material_level_hint": "strong",
        "description": "Plain cashmere crewneck.",
    }
    ev = _eval_fixture(profile, row)
    assert ev.verdict is Verdict.SUPPRESS


def test_hole_hard_rejects(profile_and_deps):
    profile, _, _ = profile_and_deps
    row = {
        "url": "fake://hole",
        "title": "Wool Jacket With Hole",
        "brand_text": "Drake's",
        "price_text": "$300",
        "shipping_text": "$20 shipping",
        "condition_text": "hole in sleeve",
        "size_text": "M",
        "category_hint": "casual jackets",
        "design_level_hint": "amazing",
        "make_quality_level_hint": "high",
        "material_level_hint": "strong",
        "description": "Rare jacket but hole.",
    }
    ev = _eval_fixture(profile, row)
    assert ev.verdict is Verdict.SUPPRESS
    assert ev.hard_reject_reason


def test_target_brand_wrong_shirt_size_hard_rejects(profile_and_deps):
    profile, _, _ = profile_and_deps
    row = {
        "url": "fake://rrl-xl",
        "title": "RRL Indigo Oxford Shirt Size XL",
        "brand_text": "RRL",
        "price_text": "$88",
        "shipping_text": "$9 shipping",
        "condition_text": "Excellent",
        "size_text": "XL",
        "category_hint": "shirts",
        "design_level_hint": "simple_tasteful",
        "make_quality_level_hint": "good",
        "material_level_hint": "good",
        "description": "Classic shirt.",
    }
    ev = _eval_fixture(profile, row)
    assert ev.verdict is Verdict.SUPPRESS


def test_poor_design_suppresses_despite_material(profile_and_deps):
    profile, _, _ = profile_and_deps
    row = {
        "url": "fake://poor-design",
        "title": "Soft Merino Crewneck Minimal Brand Size M",
        "brand_text": "Unknown Studio",
        "price_text": "$140",
        "shipping_text": "$10 shipping",
        "condition_text": "Excellent",
        "size_text": "M",
        "category_hint": "knitwear",
        "design_level_hint": "poor",
        "make_quality_level_hint": "ordinary",
        "material_level_hint": "strong",
        "description": "Soft merino but awkward silhouette.",
    }
    ev = _eval_fixture(profile, row)
    assert ev.verdict is Verdict.SUPPRESS


def test_non_target_brand_not_auto_boosted_must_earn_feed(profile_and_deps):
    profile, _, _ = profile_and_deps
    row = {
        "url": "fake://generic-overshirt",
        "title": "Generic Non-Target Cotton Overshirt",
        "brand_text": "Unknown Studio",
        "price_text": "$95",
        "shipping_text": "$8 shipping",
        "condition_text": "Very Good",
        "size_text": "M",
        "category_hint": "overshirts",
        "design_level_hint": "generic",
        "make_quality_level_hint": "ordinary",
        "material_level_hint": "good",
        "description": "Basic cotton overshirt.",
    }
    ev = _eval_fixture(profile, row)
    assert ev.verdict is Verdict.SUPPRESS
