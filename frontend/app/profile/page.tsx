"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { fetchProfileYaml, saveProfileYaml } from "@/lib/api";

export default function ProfilePage() {
  const [yaml, setYaml] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfileYaml()
      .then((r) => setYaml(r.yaml))
      .catch((e: unknown) => setErr(String(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="mx-auto max-w-3xl space-y-4 px-4 py-6">
      <h1 className="text-xl font-semibold">Buyer profile (YAML)</h1>
      <p className="text-sm text-muted-foreground">
        This file drives brands, sizes, category priorities, and price bands. Saving validates then writes to disk in the
        mounted <code className="rounded bg-muted px-1">data/</code> folder.
      </p>
      {loading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : (
        <Textarea
          className="min-h-[480px] font-mono text-xs leading-relaxed"
          value={yaml}
          onChange={(e) => setYaml(e.target.value)}
        />
      )}
      <div className="flex gap-2">
        <Button
          onClick={async () => {
            setErr(null);
            setMsg(null);
            try {
              await saveProfileYaml(yaml);
              setMsg("Saved. Re-score listings or re-run a source to apply.");
            } catch (e: unknown) {
              setErr(String(e));
            }
          }}
        >
          Save profile
        </Button>
      </div>
      {msg ? <p className="text-sm text-green-700 dark:text-green-400">{msg}</p> : null}
      {err ? <p className="text-sm text-destructive">{err}</p> : null}
    </main>
  );
}
