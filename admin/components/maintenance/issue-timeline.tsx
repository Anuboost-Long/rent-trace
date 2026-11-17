import LocalTime from "@/components/common/local-time";
import { IssueStatusLabel, IssueVisitLabel } from "@/constants/maintenance";
import type { IssueHistoryEntry } from "@/types/maintenance/models";

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
          <li key={`${entry.kind}-${entry.created_at}`} className="py-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="font-medium">
                {entry.to_status
                  ? IssueStatusLabel[entry.to_status]
                  : IssueVisitLabel[entry.kind]}
              </p>
              <p className="text-sm text-foreground/60">
                <LocalTime iso={entry.created_at} withTime />
              </p>
            </div>
            <p className="text-sm text-foreground/70">
              {entry.actor}
              {entry.on_behalf_of && `, for ${entry.on_behalf_of}`} ·{" "}
              {entry.reason}
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
