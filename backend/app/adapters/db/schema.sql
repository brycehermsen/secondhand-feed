CREATE TABLE IF NOT EXISTS sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  source_type TEXT NOT NULL,
  marketplace TEXT NOT NULL,
  config_json TEXT NOT NULL,
  cadence_minutes INTEGER,
  enabled BOOLEAN DEFAULT TRUE,
  last_run_at TEXT,
  next_run_at TEXT,
  created_at TEXT,
  updated_at TEXT
);

CREATE TABLE IF NOT EXISTS source_runs (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  status TEXT NOT NULL,
  started_at TEXT,
  finished_at TEXT,
  listings_found INTEGER DEFAULT 0,
  listings_new INTEGER DEFAULT 0,
  listings_updated INTEGER DEFAULT 0,
  error_message TEXT,
  logs_json TEXT
);

CREATE TABLE IF NOT EXISTS listings (
  id TEXT PRIMARY KEY,
  source_marketplace TEXT,
  canonical_url TEXT UNIQUE,
  source_url TEXT,
  title TEXT,
  brand_raw TEXT,
  brand_normalized TEXT,
  brand_status TEXT,
  category TEXT,
  size_raw TEXT,
  size_normalized TEXT,
  condition_raw TEXT,
  condition_normalized TEXT,
  material TEXT,
  price_item REAL,
  shipping REAL,
  all_in_price REAL,
  currency TEXT DEFAULT 'USD',
  image_url TEXT,
  description TEXT,
  seller_name TEXT,
  first_seen_at TEXT,
  last_seen_at TEXT,
  status TEXT DEFAULT 'active',
  measurements_json TEXT,
  raw_json TEXT
);

CREATE TABLE IF NOT EXISTS evaluations (
  listing_id TEXT PRIMARY KEY,
  verdict TEXT,
  score_total INTEGER,
  score_brand INTEGER,
  score_category INTEGER,
  score_design INTEGER,
  score_make_quality INTEGER,
  score_material INTEGER,
  score_price INTEGER,
  score_fit INTEGER,
  score_condition INTEGER,
  price_read TEXT,
  fit_read TEXT,
  condition_read TEXT,
  design_read TEXT,
  make_quality_read TEXT,
  material_read TEXT,
  brand_read TEXT,
  why_json TEXT,
  watchouts_json TEXT,
  seller_question TEXT,
  evaluated_at TEXT,
  model_name TEXT,
  prompt_version TEXT,
  hard_reject_reason TEXT
);

CREATE TABLE IF NOT EXISTS feed_items (
  listing_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  brand_display TEXT,
  source_marketplace TEXT,
  source_url TEXT,
  image_url TEXT,
  price_display TEXT,
  size_display TEXT,
  verdict TEXT,
  score_total INTEGER,
  design_label TEXT,
  make_quality_label TEXT,
  material_label TEXT,
  price_label TEXT,
  fit_label TEXT,
  condition_label TEXT,
  brand_read TEXT,
  why_json TEXT,
  watchouts_json TEXT,
  sort_rank INTEGER,
  is_hidden BOOLEAN DEFAULT FALSE,
  is_saved BOOLEAN DEFAULT FALSE,
  last_updated_at TEXT
);

CREATE TABLE IF NOT EXISTS user_feedback (
  id TEXT PRIMARY KEY,
  listing_id TEXT,
  action TEXT,
  reason TEXT,
  notes TEXT,
  created_at TEXT
);
