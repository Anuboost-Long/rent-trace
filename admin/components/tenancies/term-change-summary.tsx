import type { TermChange } from "@/types/tenancies/models";
import { changedRows } from "@/utils/terms";
import clsx from "clsx";
import { Check, Clock, X } from "lucide-react";

const ICON = { APPROVED: Check, DECLINED: X, WAITING: Clock } as const;

export function ChangedTerms({ change }: Readonly<{ change: TermChange }>) {
  return (
    <dl className="divide-y divide-foreground/10">
      {changedRows(change.before, change.after).map((row) => (
        <div
          key={row.label}
          className="grid gap-1 py-3 sm:grid-cols-[8rem_1fr]"
        >
          <dt className="text-sm text-foreground/60">{row.label}</dt>
          <dd>
            <span className="text-foreground/60">{row.before}</span>
            <span className="text-foreground/60"> to </span>
            <span className="font-medium">{row.after}</span>
          </dd>
        </div>
      ))}
    </dl>
  );
}

export function Approvals({ change }: Readonly<{ change: TermChange }>) {
  if (change.approvals.length === 0) return null;
  return (
    <ul className="space-y-1.5 text-sm">
      {change.approvals.map((person) => {
        const state = person.decision ?? "WAITING";
        const Icon = ICON[state];
        return (
          <li
            key={person.name}
            className={clsx(
              "flex items-center gap-2",
              person.decision ? "text-foreground" : "text-foreground/60",
            )}
          >
            <Icon aria-hidden className="size-4 shrink-0" />
            <span>{person.name}</span>
            <span className="text-foreground/60">
              {state === "APPROVED"
                ? "approved"
                : state === "DECLINED"
                  ? "declined"
                  : "has not answered"}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
