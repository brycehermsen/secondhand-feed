"use client";

import { useCallback, useEffect, useState } from "react";

import { ListingCard } from "@/components/ListingCard";
import { ListingDetailSheet } from "@/components/ListingDetailSheet";
import { fetchFeed, fetchListingDetail, postFeedback, rescoreListing, type FeedItem, type ListingDetail } from "@/lib/api";

export default function SavedPage() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ListingDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const reload = useCallback(async () => {
    setError(null);
    const data = await fetchFeed({ saved_only: true, include_hidden: true });
    setItems(data.items);
  }, []);

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

  async function wrap(fn: () => Promise<unknown>) {
    try {
      await fn();
      await reload();
      if (selectedId && sheetOpen) {
        setDetail(await fetchListingDetail(selectedId));
      }
    } catch (e: unknown) {
      setError(String(e));
    }
  }

  return (
    <>
      <main className="mx-auto max-w-6xl space-y-6 px-4 py-6">
        <h1 className="text-xl font-semibold">Saved</h1>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing saved yet.</p>
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
                onSave={() => wrap(() => postFeedback(item.listing_id, item.is_saved ? "unsave" : "save"))}
                onHide={() => wrap(() => postFeedback(item.listing_id, "hide"))}
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
        onRescore={() => selectedId && wrap(() => rescoreListing(selectedId))}
        onSaveToggle={() =>
          selectedId && wrap(() => postFeedback(selectedId, detail?.is_saved ? "unsave" : "save"))
        }
        onHide={() => selectedId && wrap(() => postFeedback(selectedId, "hide"))}
      />
    </>
  );
}
