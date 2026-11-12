import { IssueStatusLabel } from "@/constants/maintenance";
import type { IssueHistoryEntry } from "@/types/maintenance/models";
import { formatDateTime } from "@/utils/format-date";

export default function IssueTimeline({
  history,
}: Readonly<{ history: IssueHistoryEntry[] }>) {
  return (
    <section aria-labelledby="timeline-heading" className="mt-12">
      <h2 id="timeline-heading" className="text-lg font-semibold">
        History
      </h2>
      <ol className="mt-2 divide-y divide-foreground/10">
        {history.map((entry) => (
          <li key={entry.sequence_no} className="py-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="font-medium">{IssueStatusLabel[entry.to_status]}</p>
              <p className="text-sm text-foreground/60">
                {formatDateTime(entry.created_at)}
              </p>
            </div>
            <p className="text-sm text-foreground/70">
              {entry.actor} · {entry.reason}
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
