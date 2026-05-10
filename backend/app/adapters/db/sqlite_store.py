from __future__ import annotations

import json
from datetime import datetime, timezone

import sqlite3

from app.adapters.db.connection import json_dumps, json_loads
from app.domain.models import (
    Evaluation,
    FeedbackEvent,
    FeedItem,
    Listing,
    SourceConfig,
    SourceRun,
)
from app.domain.models.enums import DesignLevel, MakeQualityLevel, MaterialLevel, Verdict


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _listing_dump(listing: Listing) -> dict:
    d = listing.model_dump(mode="json")
    return d


def _listing_from_row(row: sqlite3.Row, raw: dict | None) -> Listing:
    data = dict(row)
    merged = {**data, **(raw or {})}
    if merged.get("measurements") in (None, {}) and row["measurements_json"]:
        merged["measurements"] = json_loads(row["measurements_json"])
    dl = merged.get("design_level")
    ml = merged.get("make_quality_level")
    mat = merged.get("material_level")
    return Listing(
        id=merged["id"],
        source_marketplace=merged.get("source_marketplace"),
        canonical_url=merged["canonical_url"],
        source_url=merged.get("source_url"),
        title=merged["title"],
        brand_raw=merged.get("brand_raw"),
        brand_normalized=merged.get("brand_normalized"),
        brand_status=merged.get("brand_status"),
        category=merged.get("category"),
        size_raw=merged.get("size_raw"),
        size_normalized=merged.get("size_normalized"),
        condition_raw=merged.get("condition_raw"),
        condition_normalized=merged.get("condition_normalized"),
        material=merged.get("material"),
        price_item=merged.get("price_item"),
        shipping=merged.get("shipping"),
        all_in_price=merged.get("all_in_price"),
        currency=merged.get("currency") or "USD",
        image_url=merged.get("image_url"),
        description=merged.get("description"),
        seller_name=merged.get("seller_name"),
        price_text=merged.get("price_text"),
        shipping_text=merged.get("shipping_text"),
        measurements=merged.get("measurements"),
        design_level=DesignLevel(dl) if dl else None,
        make_quality_level=MakeQualityLevel(ml) if ml else None,
        material_level=MaterialLevel(mat) if mat else None,
    )


class SqliteListingRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_listing(self, listing: Listing, raw_json: dict) -> None:
        d = _listing_dump(listing)
        measurements = d.pop("measurements", None)
        payload = {**raw_json, **d}
        self.conn.execute(
            """
            INSERT INTO listings (
              id, source_marketplace, canonical_url, source_url, title,
              brand_raw, brand_normalized, brand_status, category,
              size_raw, size_normalized, condition_raw, condition_normalized,
              material, price_item, shipping, all_in_price, currency,
              image_url, description, seller_name,
              first_seen_at, last_seen_at, status,
              measurements_json, raw_json
            ) VALUES (
              :id, :source_marketplace, :canonical_url, :source_url, :title,
              :brand_raw, :brand_normalized, :brand_status, :category,
              :size_raw, :size_normalized, :condition_raw, :condition_normalized,
              :material, :price_item, :shipping, :all_in_price, :currency,
              :image_url, :description, :seller_name,
              COALESCE((SELECT first_seen_at FROM listings WHERE id = :id), :now),
              :now,
              'active',
              :measurements_json,
              :raw_json
            )
            ON CONFLICT(id) DO UPDATE SET
              source_marketplace=excluded.source_marketplace,
              canonical_url=excluded.canonical_url,
              source_url=excluded.source_url,
              title=excluded.title,
              brand_raw=excluded.brand_raw,
              brand_normalized=excluded.brand_normalized,
              brand_status=excluded.brand_status,
              category=excluded.category,
              size_raw=excluded.size_raw,
              size_normalized=excluded.size_normalized,
              condition_raw=excluded.condition_raw,
              condition_normalized=excluded.condition_normalized,
              material=excluded.material,
              price_item=excluded.price_item,
              shipping=excluded.shipping,
              all_in_price=excluded.all_in_price,
              currency=excluded.currency,
              image_url=excluded.image_url,
              description=excluded.description,
              seller_name=excluded.seller_name,
              last_seen_at=excluded.last_seen_at,
              measurements_json=excluded.measurements_json,
              raw_json=excluded.raw_json
            ;
            """,
            {
                "id": listing.id,
                "source_marketplace": listing.source_marketplace,
                "canonical_url": listing.canonical_url,
                "source_url": listing.source_url,
                "title": listing.title,
                "brand_raw": listing.brand_raw,
                "brand_normalized": listing.brand_normalized,
                "brand_status": listing.brand_status,
                "category": listing.category,
                "size_raw": listing.size_raw,
                "size_normalized": listing.size_normalized,
                "condition_raw": listing.condition_raw,
                "condition_normalized": listing.condition_normalized,
                "material": listing.material,
                "price_item": listing.price_item,
                "shipping": listing.shipping,
                "all_in_price": listing.all_in_price,
                "currency": listing.currency,
                "image_url": listing.image_url,
                "description": listing.description,
                "seller_name": listing.seller_name,
                "measurements_json": json_dumps(measurements),
                "raw_json": json_dumps(payload),
                "now": _iso_now(),
            },
        )
        self.conn.commit()

    def get_listing(self, listing_id: str) -> Listing | None:
        row = self.conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
        if not row:
            return None
        raw = json_loads(row["raw_json"])
        if isinstance(raw, dict):
            return _listing_from_row(row, raw)
        return _listing_from_row(row, None)


class SqliteEvaluationRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_evaluation(self, evaluation: Evaluation, evaluated_at: str) -> None:
        s = evaluation.score
        self.conn.execute(
            """
            INSERT INTO evaluations (
              listing_id, verdict, score_total,
              score_brand, score_category, score_design, score_make_quality,
              score_material, score_price, score_fit, score_condition,
              price_read, fit_read, condition_read,
              design_read, make_quality_read, material_read, brand_read,
              why_json, watchouts_json, seller_question,
              evaluated_at, hard_reject_reason
            ) VALUES (
              :listing_id, :verdict, :score_total,
              :score_brand, :score_category, :score_design, :score_make_quality,
              :score_material, :score_price, :score_fit, :score_condition,
              :price_read, :fit_read, :condition_read,
              :design_read, :make_quality_read, :material_read, :brand_read,
              :why_json, :watchouts_json, :seller_question,
              :evaluated_at, :hard_reject_reason
            )
            ON CONFLICT(listing_id) DO UPDATE SET
              verdict=excluded.verdict,
              score_total=excluded.score_total,
              score_brand=excluded.score_brand,
              score_category=excluded.score_category,
              score_design=excluded.score_design,
              score_make_quality=excluded.score_make_quality,
              score_material=excluded.score_material,
              score_price=excluded.score_price,
              score_fit=excluded.score_fit,
              score_condition=excluded.score_condition,
              price_read=excluded.price_read,
              fit_read=excluded.fit_read,
              condition_read=excluded.condition_read,
              design_read=excluded.design_read,
              make_quality_read=excluded.make_quality_read,
              material_read=excluded.material_read,
              brand_read=excluded.brand_read,
              why_json=excluded.why_json,
              watchouts_json=excluded.watchouts_json,
              seller_question=excluded.seller_question,
              evaluated_at=excluded.evaluated_at,
              hard_reject_reason=excluded.hard_reject_reason
            ;
            """,
            {
                "listing_id": evaluation.listing_id,
                "verdict": evaluation.verdict.value,
                "score_total": s.total,
                "score_brand": s.brand,
                "score_category": s.category,
                "score_design": s.design,
                "score_make_quality": s.quality_of_make,
                "score_material": s.material,
                "score_price": s.price,
                "score_fit": s.fit,
                "score_condition": s.condition,
                "price_read": evaluation.price_read,
                "fit_read": evaluation.fit_read,
                "condition_read": evaluation.condition_read,
                "design_read": evaluation.design_read,
                "make_quality_read": evaluation.make_quality_read,
                "material_read": evaluation.material_read,
                "brand_read": evaluation.brand_read,
                "why_json": json_dumps(evaluation.why),
                "watchouts_json": json_dumps(evaluation.watchouts),
                "seller_question": evaluation.seller_question,
                "evaluated_at": evaluated_at,
                "hard_reject_reason": evaluation.hard_reject_reason,
            },
        )
        self.conn.commit()

    def get_evaluation(self, listing_id: str) -> Evaluation | None:
        row = self.conn.execute("SELECT * FROM evaluations WHERE listing_id = ?", (listing_id,)).fetchone()
        if not row:
            return None
        from app.domain.models.evaluation import ScoreBreakdown

        score = ScoreBreakdown(
            brand=row["score_brand"],
            category=row["score_category"],
            design=row["score_design"],
            quality_of_make=row["score_make_quality"],
            material=row["score_material"],
            price=row["score_price"],
            fit=row["score_fit"],
            condition=row["score_condition"],
            total=row["score_total"],
        )
        return Evaluation(
            listing_id=row["listing_id"],
            verdict=Verdict(row["verdict"]),
            score=score,
            price_read=row["price_read"],
            fit_read=row["fit_read"],
            condition_read=row["condition_read"],
            design_read=row["design_read"],
            make_quality_read=row["make_quality_read"],
            material_read=row["material_read"],
            brand_read=row["brand_read"],
            why=list(json_loads(row["why_json"]) or []),
            watchouts=list(json_loads(row["watchouts_json"]) or []),
            seller_question=row["seller_question"],
            hard_reject_reason=row["hard_reject_reason"],
        )


class SqliteFeedRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_feed_item(self, item: FeedItem, last_updated_at: str) -> None:
        self.conn.execute(
            """
            INSERT INTO feed_items (
              listing_id, title, brand_display, source_marketplace, source_url,
              image_url, price_display, size_display, verdict, score_total,
              design_label, make_quality_label, material_label,
              price_label, fit_label, condition_label,
              brand_read, why_json, watchouts_json,
              sort_rank, is_hidden, is_saved, last_updated_at
            ) VALUES (
              :listing_id, :title, :brand_display, :source_marketplace, :source_url,
              :image_url, :price_display, :size_display, :verdict, :score_total,
              :design_label, :make_quality_label, :material_label,
              :price_label, :fit_label, :condition_label,
              :brand_read, :why_json, :watchouts_json,
              :sort_rank, :is_hidden, :is_saved, :last_updated_at
            )
            ON CONFLICT(listing_id) DO UPDATE SET
              title=excluded.title,
              brand_display=excluded.brand_display,
              source_marketplace=excluded.source_marketplace,
              source_url=excluded.source_url,
              image_url=excluded.image_url,
              price_display=excluded.price_display,
              size_display=excluded.size_display,
              verdict=excluded.verdict,
              score_total=excluded.score_total,
              design_label=excluded.design_label,
              make_quality_label=excluded.make_quality_label,
              material_label=excluded.material_label,
              price_label=excluded.price_label,
              fit_label=excluded.fit_label,
              condition_label=excluded.condition_label,
              brand_read=excluded.brand_read,
              why_json=excluded.why_json,
              watchouts_json=excluded.watchouts_json,
              sort_rank=excluded.sort_rank,
              last_updated_at=excluded.last_updated_at
            ;
            """,
            {
                "listing_id": item.listing_id,
                "title": item.title,
                "brand_display": item.brand_display,
                "source_marketplace": item.source_marketplace,
                "source_url": item.source_url,
                "image_url": item.image_url,
                "price_display": item.price_display,
                "size_display": item.size_display,
                "verdict": item.verdict,
                "score_total": item.score_total,
                "design_label": item.design_label,
                "make_quality_label": item.make_quality_label,
                "material_label": item.material_label,
                "price_label": item.price_label,
                "fit_label": item.fit_label,
                "condition_label": item.condition_label,
                "brand_read": item.brand_read,
                "why_json": json_dumps(item.why_json),
                "watchouts_json": json_dumps(item.watchouts_json),
                "sort_rank": item.sort_rank,
                "is_hidden": int(item.is_hidden),
                "is_saved": int(item.is_saved),
                "last_updated_at": last_updated_at,
            },
        )
        self.conn.commit()

    def list_feed_items(
        self,
        *,
        verdicts: list[str] | None,
        include_hidden: bool,
        saved_only: bool,
    ) -> list[FeedItem]:
        clauses: list[str] = ["1=1"]
        params: list[object] = []
        if verdicts:
            placeholders = ",".join(["?"] * len(verdicts))
            clauses.append(f"verdict IN ({placeholders})")
            params.extend(verdicts)
        if not include_hidden:
            clauses.append("is_hidden = 0")
        if saved_only:
            clauses.append("is_saved = 1")

        sql = f"SELECT * FROM feed_items WHERE {' AND '.join(clauses)} ORDER BY sort_rank DESC, title ASC"
        rows = self.conn.execute(sql, params).fetchall()
        out: list[FeedItem] = []
        for row in rows:
            out.append(
                FeedItem(
                    listing_id=row["listing_id"],
                    title=row["title"],
                    brand_display=row["brand_display"],
                    source_marketplace=row["source_marketplace"],
                    source_url=row["source_url"],
                    image_url=row["image_url"],
                    price_display=row["price_display"],
                    size_display=row["size_display"],
                    verdict=row["verdict"],
                    score_total=row["score_total"],
                    design_label=row["design_label"],
                    make_quality_label=row["make_quality_label"],
                    material_label=row["material_label"],
                    price_label=row["price_label"],
                    fit_label=row["fit_label"],
                    condition_label=row["condition_label"],
                    brand_read=row["brand_read"],
                    why_json=list(json_loads(row["why_json"]) or []),
                    watchouts_json=list(json_loads(row["watchouts_json"]) or []),
                    sort_rank=row["sort_rank"],
                    is_hidden=bool(row["is_hidden"]),
                    is_saved=bool(row["is_saved"]),
                )
            )
        return out

    def get_feedback_flags(self, listing_id: str) -> tuple[bool, bool]:
        row = self.conn.execute(
            "SELECT is_saved, is_hidden FROM feed_items WHERE listing_id = ?",
            (listing_id,),
        ).fetchone()
        if not row:
            return False, False
        return bool(row["is_saved"]), bool(row["is_hidden"])

    def update_feedback_flags(self, listing_id: str, *, is_saved: bool | None, is_hidden: bool | None) -> None:
        fields = []
        vals: list[object] = []
        if is_saved is not None:
            fields.append("is_saved = ?")
            vals.append(int(is_saved))
        if is_hidden is not None:
            fields.append("is_hidden = ?")
            vals.append(int(is_hidden))
        if not fields:
            return
        vals.append(listing_id)
        self.conn.execute(f"UPDATE feed_items SET {', '.join(fields)} WHERE listing_id = ?", vals)
        self.conn.commit()


class SqliteFeedbackRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def append_feedback(self, event: FeedbackEvent) -> None:
        self.conn.execute(
            """
            INSERT INTO user_feedback (id, listing_id, action, reason, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event.id, event.listing_id, event.action, event.reason, event.notes, event.created_at),
        )
        self.conn.commit()


class SqliteSourceRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def upsert_source(self, source: SourceConfig, config_obj: dict) -> None:
        now = _iso_now()
        self.conn.execute(
            """
            INSERT INTO sources (id, name, source_type, marketplace, config_json, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name,
              source_type=excluded.source_type,
              marketplace=excluded.marketplace,
              config_json=excluded.config_json,
              enabled=excluded.enabled,
              updated_at=excluded.updated_at
            ;
            """,
            (
                source.id,
                source.name,
                source.source_type,
                source.marketplace,
                json.dumps(config_obj),
                int(source.enabled),
                now,
                now,
            ),
        )
        self.conn.commit()

    def get_source(self, source_id: str) -> SourceConfig | None:
        row = self.conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        if not row:
            return None
        return SourceConfig(
            id=row["id"],
            name=row["name"],
            source_type=row["source_type"],
            marketplace=row["marketplace"],
            enabled=bool(row["enabled"]),
        )

    def get_source_config(self, source_id: str) -> dict:
        row = self.conn.execute("SELECT config_json FROM sources WHERE id = ?", (source_id,)).fetchone()
        if not row:
            return {}
        raw = row["config_json"]
        return json.loads(raw) if raw else {}

    def set_source_config(self, source_id: str, cfg: dict) -> None:
        self.conn.execute(
            "UPDATE sources SET config_json = ?, updated_at = ? WHERE id = ?",
            (json.dumps(cfg), _iso_now(), source_id),
        )
        self.conn.commit()


class SqliteSourceRunRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create_run(self, run: SourceRun) -> None:
        self.conn.execute(
            """
            INSERT INTO source_runs (
              id, source_id, status, started_at, finished_at,
              listings_found, listings_new, listings_updated, error_message, logs_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run.id,
                run.source_id,
                run.status,
                run.started_at,
                run.finished_at,
                run.listings_found,
                run.listings_new,
                run.listings_updated,
                run.error_message,
                run.logs_json,
            ),
        )
        self.conn.commit()

    def finish_run(self, run_id: str, *, status: str, counts: dict[str, int], error: str | None) -> None:
        self.conn.execute(
            """
            UPDATE source_runs
            SET status = ?, finished_at = ?, listings_found = ?, listings_new = ?, listings_updated = ?, error_message = ?
            WHERE id = ?
            """,
            (
                status,
                _iso_now(),
                counts.get("found", 0),
                counts.get("new", 0),
                counts.get("updated", 0),
                error,
                run_id,
            ),
        )
        self.conn.commit()

    def list_runs(self, limit: int) -> list[SourceRun]:
        rows = self.conn.execute(
            "SELECT * FROM source_runs ORDER BY datetime(started_at) DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            SourceRun(
                id=r["id"],
                source_id=r["source_id"],
                status=r["status"],
                started_at=r["started_at"],
                finished_at=r["finished_at"],
                listings_found=r["listings_found"],
                listings_new=r["listings_new"],
                listings_updated=r["listings_updated"],
                error_message=r["error_message"],
                logs_json=r["logs_json"],
            )
            for r in rows
        ]
