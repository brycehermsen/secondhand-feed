"use client";

import { useEffect, useState } from "react";

import { fetchRuns } from "@/lib/api";

type RunRow = {
  id: string;
  source_id: string;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  listings_found: number;
  listings_new: number;
  listings_updated: number;
  error_message: string | null;
};

export default function RunsPage() {
  const [runs, setRuns] = useState<RunRow[]>([]);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchRuns()
      .then((r: { runs: RunRow[] }) => setRuns(r.runs))
      .catch((e: unknown) => setErr(String(e)));
  }, []);

  return (
    <main className="mx-auto max-w-5xl space-y-4 px-4 py-6">
      <h1 className="text-xl font-semibold">Source runs</h1>
      {err ? <p className="text-sm text-destructive">{err}</p> : null}
      <div className="overflow-x-auto rounded-md border">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-muted/50 text-xs uppercase text-muted-foreground">
            <tr>
              <th className="px-3 py-2">Status</th>
              <th className="px-3 py-2">Source</th>
              <th className="px-3 py-2">Found</th>
              <th className="px-3 py-2">New</th>
              <th className="px-3 py-2">Updated</th>
              <th className="px-3 py-2">Started</th>
              <th className="px-3 py-2">Error</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((r) => (
              <tr key={r.id} className="border-b last:border-0">
                <td className="px-3 py-2 font-medium">{r.status}</td>
                <td className="px-3 py-2 text-muted-foreground">{r.source_id}</td>
                <td className="px-3 py-2">{r.listings_found}</td>
                <td className="px-3 py-2">{r.listings_new}</td>
                <td className="px-3 py-2">{r.listings_updated}</td>
                <td className="px-3 py-2 text-xs text-muted-foreground">{r.started_at ?? "—"}</td>
                <td className="max-w-xs truncate px-3 py-2 text-xs text-destructive">{r.error_message ?? ""}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
