import { TermChangeStatusLabel } from "@/constants/tenancies";
import type { TermChange } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import { changedRows } from "@/utils/terms";

export default function TermHistory({
  changes,
}: Readonly<{ changes: TermChange[] }>) {
  const rows = changes.filter(
    (change) => changedRows(change.before, change.after).length > 0,
  );
  if (rows.length === 0) return null;

  return (
    <section aria-labelledby="term-history-heading" className="mt-12">
      <h2 id="term-history-heading" className="text-lg font-semibold">
        Rent and bond history
      </h2>
      <ul className="mt-2 divide-y divide-foreground/10">
        {rows.map((change) => (
          <li key={change.id} className="py-3">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="text-sm text-foreground/60">
                {formatDate(change.decided_at ?? change.created_at)}
                {change.proposed_by && ` by ${change.proposed_by}`}
              </p>
              <p className="text-sm text-foreground/60">
                {TermChangeStatusLabel[change.status]}
              </p>
            </div>
            {changedRows(change.before, change.after).map((row) => (
              <p key={row.label} className="mt-1">
                <span className="text-foreground/60">{row.label} </span>
                {row.before}
                <span className="text-foreground/60"> to </span>
                <span className="font-medium">{row.after}</span>
              </p>
            ))}
          </li>
        ))}
      </ul>
    </section>
  );
}
