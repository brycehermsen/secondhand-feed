"use client";

import Image from "next/image";

import type { ListingDetail } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

type Props = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  detail: ListingDetail | null;
  loading?: boolean;
  onRescore: () => void;
  onSaveToggle: () => void;
  onHide: () => void;
};

export function ListingDetailSheet({
  open,
  onOpenChange,
  detail,
  loading,
  onRescore,
  onSaveToggle,
  onHide,
}: Props) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="flex w-full flex-col gap-0 overflow-hidden sm:max-w-lg">
        <SheetHeader className="pb-2">
          <SheetTitle className="line-clamp-2 pr-8">{detail?.title ?? "Listing"}</SheetTitle>
        </SheetHeader>
        {loading || !detail ? (
          <p className="p-4 text-sm text-muted-foreground">Loading…</p>
        ) : (
          <>
            <div className="relative mx-auto aspect-[3/4] w-full max-w-xs overflow-hidden rounded-md bg-muted">
              {detail.image_url ? (
                <Image src={detail.image_url} alt="" fill className="object-cover" unoptimized />
              ) : (
                <div className="flex h-full items-center justify-center text-xs text-muted-foreground">No image</div>
              )}
            </div>
            <ScrollArea className="mt-4 h-[calc(100vh-220px)] pr-4">
              <div className="flex flex-wrap gap-2 pb-3">
                <Badge>{detail.verdict_label}</Badge>
                <Badge variant="outline">{detail.score_total}/50</Badge>
                {detail.hard_reject_reason ? <Badge variant="destructive">Hard reject</Badge> : null}
              </div>
              <div className="space-y-1 text-sm">
                <p className="text-muted-foreground">{detail.brand}</p>
                <p>{detail.price_display}</p>
                <p className="text-muted-foreground">Size {detail.size_display ?? "—"}</p>
              </div>
              <Separator className="my-4" />
              <div className="space-y-2 text-sm">
                <h4 className="font-medium">Score breakdown</h4>
                <ul className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-muted-foreground">
                  {Object.entries(detail.score_breakdown).map(([k, v]) => (
                    <li key={k} className="flex justify-between gap-2">
                      <span className="capitalize">{k.replace(/_/g, " ")}</span>
                      <span className="text-foreground">{v}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <Separator className="my-4" />
              <div className="space-y-3 text-sm">
                <div>
                  <h4 className="font-medium">Reads</h4>
                  <ul className="mt-1 space-y-1 text-xs text-muted-foreground">
                    {Object.entries(detail.reads).map(([k, v]) => (
                      <li key={k}>
                        <span className="font-medium text-foreground">{k}: </span>
                        {v}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Why</h4>
                  <ul className="mt-1 list-disc space-y-1 pl-4 text-xs text-muted-foreground">
                    {detail.why.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
                {detail.watchouts.length ? (
                  <div>
                    <h4 className="font-medium text-amber-700 dark:text-amber-400">Watch-outs</h4>
                    <ul className="mt-1 list-disc space-y-1 pl-4 text-xs">
                      {detail.watchouts.map((w, i) => (
                        <li key={i}>{w}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {detail.seller_question ? (
                  <div className="rounded-md border bg-muted/40 p-3 text-xs">
                    <span className="font-medium">Ask the seller: </span>
                    {detail.seller_question}
                  </div>
                ) : null}
              </div>
            </ScrollArea>
            <div className="mt-auto flex flex-wrap gap-2 border-t pt-4">
              <Button size="sm" variant="secondary" onClick={onRescore}>
                Re-score
              </Button>
              <Button size="sm" variant="outline" onClick={onSaveToggle}>
                {detail.is_saved ? "Unsave" : "Save"}
              </Button>
              <Button size="sm" variant="ghost" onClick={onHide}>
                Hide
              </Button>
              {detail.source_url ? (
                <a
                  href={detail.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className={cn(buttonVariants({ size: "sm" }))}
                >
                  Open listing
                </a>
              ) : null}
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
