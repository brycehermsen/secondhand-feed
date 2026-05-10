"use client";

import Image from "next/image";

import type { FeedItem } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";

function verdictVariant(v: string): "default" | "secondary" | "destructive" | "outline" {
  if (v === "click_now") return "default";
  if (v === "maybe") return "secondary";
  if (v === "only_if_you_love_it") return "outline";
  return "destructive";
}

type Props = {
  item: FeedItem;
  onOpen: () => void;
  onSave: () => void;
  onHide: () => void;
  onUnhide: () => void;
};

export function ListingCard({ item, onOpen, onSave, onHide, onUnhide }: Props) {
  const watch = item.watchouts_json[0];

  return (
    <Card className="flex flex-col overflow-hidden">
      <div className="relative aspect-[4/5] w-full bg-muted">
        {item.image_url ? (
          <Image
            src={item.image_url}
            alt=""
            fill
            className="object-cover"
            sizes="(max-width:768px) 100vw, 33vw"
            unoptimized
          />
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">No image</div>
        )}
      </div>
      <CardHeader className="space-y-2 pb-2">
        <div className="flex flex-wrap gap-1">
          <Badge variant={verdictVariant(item.verdict)}>{item.verdict.replace(/_/g, " ")}</Badge>
          <Badge variant="outline">{item.score_total}/50</Badge>
          {item.is_saved ? <Badge variant="secondary">Saved</Badge> : null}
          {item.is_hidden ? <Badge variant="outline">Hidden</Badge> : null}
        </div>
        <div>
          <p className="text-xs uppercase text-muted-foreground">{item.brand_display ?? "Brand unknown"}</p>
          <h3 className="line-clamp-2 text-sm font-medium leading-snug">{item.title}</h3>
        </div>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-2 pb-2 text-xs text-muted-foreground">
        <div className="flex flex-wrap gap-x-3 gap-y-1">
          <span>{item.price_display}</span>
          {item.size_display ? <span>Size {item.size_display}</span> : null}
          {item.source_marketplace ? <span className="capitalize">{item.source_marketplace}</span> : null}
        </div>
        <div className="grid grid-cols-2 gap-1 text-[11px] leading-snug">
          <span title="Design">{item.design_label}</span>
          <span title="Make">{item.make_quality_label}</span>
          <span title="Material">{item.material_label}</span>
          <span title="Price read">{item.price_label}</span>
          <span title="Fit read">{item.fit_label}</span>
          <span title="Condition read" className="line-clamp-2">
            {item.condition_label}
          </span>
        </div>
        {item.why_json[0] ? <p className="line-clamp-3 text-foreground/90">{item.why_json[0]}</p> : null}
        {watch ? <p className="text-amber-700 dark:text-amber-400">Watch-out: {watch}</p> : null}
      </CardContent>
      <CardFooter className="flex flex-wrap gap-2 border-t bg-muted/40 pt-3">
        <Button size="sm" variant="secondary" onClick={onOpen}>
          Details
        </Button>
        <Button size="sm" variant="outline" onClick={onSave}>
          {item.is_saved ? "Unsave" : "Save"}
        </Button>
        <Button size="sm" variant="ghost" onClick={item.is_hidden ? onUnhide : onHide}>
          {item.is_hidden ? "Unhide" : "Hide"}
        </Button>
      </CardFooter>
    </Card>
  );
}
