from __future__ import annotations

import hashlib

from app.domain.models.buyer_profile import BuyerProfile
from app.domain.models.enums import Verdict
from app.domain.models.evaluation import Evaluation, ScoreBreakdown
from app.domain.models.listing import EvalListingInput, Listing, RawListingSummary
from app.domain.normalization import (
    normalize_brand,
    normalize_category,
    normalize_condition,
    normalize_price,
    normalize_size,
)
from app.domain.evaluation import (
    apply_hard_filters,
    cheap_boost_material_domination,
    clamp_total,
    parse_design_hint,
    parse_make_hint,
    parse_material_hint,
    score_brand,
    score_category,
    score_condition,
    score_design,
    score_fit,
    score_make_quality,
    score_material,
    score_price,
    surface_verdict_override,
    verdict_from_total,
)


def listing_id_from_url(url: str) -> str:
    return "lst_" + hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]


def listing_and_eval_input_from_raw(raw: RawListingSummary, listing_id: str, profile: BuyerProfile) -> EvalListingInput:
    """Normalize listing fields from a connector payload using the active buyer profile."""

    brand_n = normalize_brand(raw.brand_text, raw.title, profile)
    cat_n = normalize_category(raw.title, raw.category_hint, profile)
    size_n = normalize_size(raw.size_text, raw.title, cat_n.category_key, profile)
    cond_n = normalize_condition(raw.condition_text, raw.title, raw.description, profile)
    price_n = normalize_price(raw.price_text, raw.shipping_text)

    listing = Listing(
        id=listing_id,
        source_marketplace=raw.marketplace,
        canonical_url=raw.canonical_url,
        source_url=raw.canonical_url,
        title=raw.title,
        brand_raw=raw.brand_text,
        brand_normalized=brand_n.normalized_brand,
        brand_status=brand_n.status.value,
        category=cat_n.category_key,
        size_raw=raw.size_text,
        size_normalized=" ".join(size_n.normalized_tokens) if size_n.normalized_tokens else (raw.size_text or ""),
        condition_raw=raw.condition_text,
        condition_normalized=cond_n.level.value,
        material=None,
        price_item=price_n.item_price,
        shipping=price_n.shipping,
        all_in_price=price_n.all_in,
        currency=price_n.currency,
        image_url=raw.image_url,
        description=raw.description,
        seller_name=raw.seller_name,
        price_text=raw.price_text,
        shipping_text=raw.shipping_text,
        measurements=raw.measurements,
        design_level=parse_design_hint(raw.design_level_hint),
        make_quality_level=parse_make_hint(raw.make_quality_level_hint),
        material_level=parse_material_hint(raw.material_level_hint),
    )

    return EvalListingInput(
        listing=listing,
        design_hint=raw.design_level_hint,
        make_hint=raw.make_quality_level_hint,
        material_hint=raw.material_level_hint,
    )


def evaluate_eval_input(inp: EvalListingInput, profile: BuyerProfile) -> Evaluation:
    listing = inp.listing

    brand_n = normalize_brand(listing.brand_raw, listing.title, profile)
    cat_n = normalize_category(listing.title, listing.category, profile)
    size_n = normalize_size(listing.size_raw, listing.title, cat_n.category_key, profile)
    cond_n = normalize_condition(listing.condition_raw, listing.title, listing.description, profile)

    price_all_in = listing.all_in_price
    if price_all_in is None:
        pn = normalize_price(listing.price_text, listing.shipping_text)
        price_all_in = pn.all_in

    hf = apply_hard_filters(
        title=listing.title,
        description=listing.description,
        brand=brand_n,
        condition_norm=cond_n,
        size_norm=size_n,
        category_key=cat_n.category_key,
        profile=profile,
    )
    if hf.reject:
        zero = ScoreBreakdown(
            brand=0,
            category=0,
            design=0,
            quality_of_make=0,
            material=0,
            price=0,
            fit=0,
            condition=0,
            total=0,
        )
        return Evaluation(
            listing_id=listing.id,
            verdict=Verdict.SUPPRESS,
            score=zero,
            price_read="bad",
            fit_read="bad",
            condition_read=cond_n.read,
            design_read="n/a",
            make_quality_read="n/a",
            material_read="n/a",
            brand_read=brand_n.read,
            why=[hf.reason or "Hard filtered."],
            watchouts=["Hard reject"],
            seller_question=None,
            hard_reject_reason=hf.reason,
        )

    design = parse_design_hint(inp.design_hint) if inp.design_hint else (listing.design_level or parse_design_hint(None))
    make = parse_make_hint(inp.make_hint) if inp.make_hint else (listing.make_quality_level or parse_make_hint(None))
    material = parse_material_hint(inp.material_hint) if inp.material_hint else (listing.material_level or parse_material_hint(None))

    b_pts, b_read = score_brand(brand_n)
    c_pts, c_read = score_category(cat_n)
    d_pts, d_read = score_design(design)
    m_pts, m_read = score_make_quality(make)
    mat_pts, mat_read = score_material(material)
    cond_pts, cond_read = score_condition(cond_n, profile)
    fit_pts, fit_enum, fit_read = score_fit(size_n, listing.measurements, cat_n.category_key)

    p_pts, price_read, price_read_txt = score_price(
        all_in=price_all_in,
        category_key=cat_n.category_key,
        design=design,
        make=make,
        material=material,
        title=listing.title,
        description=listing.description,
        profile=profile,
    )

    parts = {
        "brand": b_pts,
        "category": c_pts,
        "design": d_pts,
        "quality_of_make": m_pts,
        "material": mat_pts,
        "price": p_pts,
        "fit": fit_pts,
        "condition": cond_pts,
    }
    parts = cheap_boost_material_domination(brand_n, parts, price_read, material)
    breakdown = clamp_total(parts)

    override = surface_verdict_override(
        design=design,
        make=make,
        all_in=price_all_in,
        profile=profile,
        category_key=cat_n.category_key,
        brand_status=brand_n.status,
        price_read=price_read,
        total_before_clamp=breakdown.total,
    )
    verdict = override or verdict_from_total(breakdown.total)

    why = [b_read, c_read, d_read, m_read, mat_read, price_read_txt, fit_read, cond_read]

    watchouts: list[str] = []
    if listing.measurements in (None, {}) and any(
        k in cat_n.category_key.lower() for k in ("jacket", "coat", "shirt", "trouser", "pant")
    ):
        watchouts.append("No measurements provided; tailoring risk.")

    seller_q = None
    if brand_n.status.value == "unknown" and d_pts >= 7:
        seller_q = "Ask whether fabric composition and country of manufacture match listing assumptions."

    return Evaluation(
        listing_id=listing.id,
        verdict=verdict,
        score=breakdown,
        price_read=price_read.value,
        fit_read=fit_enum.value,
        condition_read=cond_read,
        design_read=d_read,
        make_quality_read=m_read,
        material_read=mat_read,
        brand_read=b_read,
        why=why,
        watchouts=watchouts,
        seller_question=seller_q,
        hard_reject_reason=None,
    )
