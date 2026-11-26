import { labelOptions, PropertyTypeLabel } from "@/constants/properties";
import { Route } from "@/constants/web-routes";
import Link from "next/link";

const TYPES = labelOptions(PropertyTypeLabel).filter(
  (option) => option.value !== "OTHER",
);

export default function BrowseByType() {
  return (
    <nav aria-label="Browse by type" className="mt-5">
      <ul className="flex flex-wrap gap-2">
        {TYPES.map((type) => (
          <li key={type.value}>
            <Link
              href={`${Route.listings}?${new URLSearchParams({ type: type.value })}`}
              className="inline-flex h-9 items-center rounded-full border border-default px-4 text-sm font-medium hover:bg-subtle focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
            >
              {type.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
