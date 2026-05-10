"use client";

import { useCallback, useEffect, useState } from "react";

import { ListingCard } from "@/components/ListingCard";
import { ListingDetailSheet } from "@/components/ListingDetailSheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  fetchFeed,
  fetchListingDetail,
  postFeedback,
  rescoreListing,
  runEbaySearch,
  runFakeSource,
  type FeedItem,
  type ListingDetail,
} from "@/lib/api";

export default function FeedPage() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [includeOiyli, setIncludeOiyli] = useState(false);
  const [includeSuppressed, setIncludeSuppressed] = useState(false);
  const [includeHidden, setIncludeHidden] = useState(false);
  const [ebayQuery, setEbayQuery] = useState("drakes chore coat");
  const [ebayLimit, setEbayLimit] = useState(15);

  const [sheetOpen, setSheetOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ListingDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const reload = useCallback(async () => {
    setError(null);
    const data = await fetchFeed({
      include_oiyli: includeOiyli,
      include_suppressed: includeSuppressed,
      include_hidden: includeHidden,
    });
    setItems(data.items);
  }, [includeHidden, includeOiyli, includeSuppressed]);

  useEffect(() => {
    reload().catch((e: unknown) => setError(String(e)));
  }, [reload]);

  useEffect(() => {
    if (!sheetOpen || !selectedId) return;
    setDetailLoading(true);
    fetchListingDetail(selectedId)
      .then(setDetail)
      .catch((e: unknown) => setError(String(e)))
      .finally(() => setDetailLoading(false));
  }, [sheetOpen, selectedId]);

  async function wrap(task: string, fn: () => Promise<unknown>) {
    setBusy(task);
    setError(null);
    try {
      await fn();
      await reload();
      if (selectedId && sheetOpen) {
        setDetailLoading(true);
        setDetail(await fetchListingDetail(selectedId));
        setDetailLoading(false);
      }
    } catch (e: unknown) {
      setError(String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <>
      <main className="mx-auto max-w-6xl space-y-6 px-4 py-6">
        <div className="flex flex-col gap-4 rounded-lg border bg-card p-4 shadow-sm">
          <div className="flex flex-wrap items-end gap-3">
            <Button disabled={!!busy} onClick={() => wrap("fake", runFakeSource)}>
              Run fake source
            </Button>
            <div className="flex flex-1 flex-wrap items-end gap-2">
              <div className="min-w-[200px] flex-1 space-y-1">
                <Label htmlFor="ebay-q">eBay search</Label>
                <Input id="ebay-q" value={ebayQuery} onChange={(e) => setEbayQuery(e.target.value)} />
              </div>
              <div className="w-24 space-y-1">
                <Label htmlFor="ebay-lim">Limit</Label>
                <Input
                  id="ebay-lim"
                  type="number"
                  min={1}
                  max={50}
                  value={ebayLimit}
                  onChange={(e) => setEbayLimit(Number(e.target.value))}
                />
              </div>
              <Button
                variant="secondary"
                disabled={!!busy}
                onClick={() => wrap("ebay", () => runEbaySearch(ebayQuery, ebayLimit))}
              >
                Run eBay search
              </Button>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 text-sm">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={includeOiyli} onChange={(e) => setIncludeOiyli(e.target.checked)} />
              Show “only if you love it”
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={includeSuppressed} onChange={(e) => setIncludeSuppressed(e.target.checked)} />
              Show suppressed
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={includeHidden} onChange={(e) => setIncludeHidden(e.target.checked)} />
              Show hidden
            </label>
          </div>
          {busy ? <p className="text-xs text-muted-foreground">Working: {busy}…</p> : null}
          {error ? <p className="text-sm text-destructive">{error}</p> : null}
        </div>

        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No feed items yet. Run the fake source (or an eBay search with credentials) to import listings.
          </p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => (
              <ListingCard
                key={item.listing_id}
                item={item}
                onOpen={() => {
                  setSelectedId(item.listing_id);
                  setSheetOpen(true);
                }}
                onSave={() =>
                  wrap("save", () => postFeedback(item.listing_id, item.is_saved ? "unsave" : "save"))
                }
                onHide={() => wrap("hide", () => postFeedback(item.listing_id, "hide"))}
              />
            ))}
          </div>
        )}
      </main>

      <ListingDetailSheet
        open={sheetOpen}
        onOpenChange={setSheetOpen}
        detail={detail}
        loading={detailLoading}
        onRescore={() => selectedId && wrap("rescore", () => rescoreListing(selectedId))}
        onSaveToggle={() =>
          selectedId &&
          wrap("save", () => postFeedback(selectedId, detail?.is_saved ? "unsave" : "save"))
        }
        onHide={() => selectedId && wrap("hide", () => postFeedback(selectedId, "hide"))}
      />
    </>
  );
}
