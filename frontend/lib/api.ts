const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type FeedItem = {
  listing_id: string;
  title: string;
  brand_display: string | null;
  source_marketplace: string | null;
  source_url: string | null;
  image_url: string | null;
  price_display: string;
  size_display: string | null;
  verdict: string;
  score_total: number;
  design_label: string;
  make_quality_label: string;
  material_label: string;
  price_label: string;
  fit_label: string;
  condition_label: string;
  brand_read: string;
  why_json: string[];
  watchouts_json: string[];
  sort_rank: number;
  is_hidden: boolean;
  is_saved: boolean;
};

export type ListingDetail = {
  listing_id: string;
  title: string;
  brand: string | null;
  source_marketplace: string | null;
  source_url: string | null;
  image_url: string | null;
  price_display: string;
  size_display: string | null;
  verdict: string;
  verdict_label: string;
  score_total: number;
  score_breakdown: Record<string, number>;
  reads: Record<string, string>;
  labels: Record<string, string>;
  why: string[];
  watchouts: string[];
  seller_question: string | null;
  hard_reject_reason: string | null;
  is_saved: boolean;
  is_hidden: boolean;
  measurements: Record<string, string>;
};

async function handle(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    return res.json();
  }
  return res.text();
}

export async function fetchFeed(params: {
  include_oiyli?: boolean;
  include_suppressed?: boolean;
  include_hidden?: boolean;
  saved_only?: boolean;
}): Promise<{ items: FeedItem[] }> {
  const q = new URLSearchParams();
  if (params.include_oiyli) q.set("include_oiyli", "true");
  if (params.include_suppressed) q.set("include_suppressed", "true");
  if (params.include_hidden) q.set("include_hidden", "true");
  if (params.saved_only) q.set("saved_only", "true");
  const res = await fetch(`${API_BASE}/api/feed?${q.toString()}`, { cache: "no-store" });
  return handle(res);
}

export async function fetchListingDetail(id: string): Promise<ListingDetail> {
  const res = await fetch(`${API_BASE}/api/listings/${id}`, { cache: "no-store" });
  return handle(res);
}

export async function runFakeSource() {
  const res = await fetch(`${API_BASE}/api/sources/fake/run`, { method: "POST" });
  return handle(res);
}

export async function runEbaySearch(query: string, limit: number) {
  const res = await fetch(`${API_BASE}/api/sources/ebay/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, limit }),
  });
  return handle(res);
}

export async function fetchProfileYaml(): Promise<{ yaml: string }> {
  const res = await fetch(`${API_BASE}/api/profile`, { cache: "no-store" });
  return handle(res);
}

export async function saveProfileYaml(yaml: string) {
  const res = await fetch(`${API_BASE}/api/profile`, {
    method: "PUT",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: yaml,
  });
  return handle(res);
}

export async function postFeedback(listingId: string, action: string) {
  const res = await fetch(`${API_BASE}/api/listings/${listingId}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action }),
  });
  return handle(res);
}

export async function rescoreListing(listingId: string) {
  const res = await fetch(`${API_BASE}/api/listings/${listingId}/rescore`, { method: "POST" });
  return handle(res);
}

export async function fetchRuns(limit = 50) {
  const res = await fetch(`${API_BASE}/api/runs?limit=${limit}`, { cache: "no-store" });
  return handle(res);
}

export function apiBase() {
  return API_BASE;
}
