import clsx from "clsx";
import Link from "next/link";

export type FilterChip = {
  label: string;
  href: string;
  count?: number;
  active: boolean;
};

type FilterChipsProp = Readonly<{ label: string; chips: FilterChip[] }>;

export default function FilterChips({ label, chips }: FilterChipsProp) {
  return (
    <nav aria-label={label}>
      <ul className="flex flex-wrap gap-2">
        {chips.map((chip) => (
          <li key={chip.label}>
            <Link
              href={chip.href}
              aria-current={chip.active ? "page" : undefined}
              className={clsx(
                "inline-flex h-9 items-center rounded-full border px-4 text-body-sm transition-colors motion-reduce:transition-none",
                "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border",
                chip.active
                  ? "border-2 border-brand-border bg-brand-subtle font-semibold text-admin-text"
                  : "border-strong bg-background text-fg-primary hover:bg-subtle",
              )}
            >
              {chip.label}
              {chip.count !== undefined && ` · ${chip.count.toLocaleString()}`}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
