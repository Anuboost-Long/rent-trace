import ButtonLink from "@/components/common/button-link";
import { ArrowLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

export type Crumb = { label: string; href?: string };

type BreadcrumbsProp = Readonly<{ trail: Crumb[] }>;

export default function Breadcrumbs({ trail }: BreadcrumbsProp) {
  const parent = trail.at(-2);

  return (
    <div className="flex flex-col items-start gap-3">
      {parent?.href && (
        <ButtonLink
          href={parent.href}
          variant="quiet"
          size="sm"
          aria-label={`Back to ${parent.label}`}
          className="gap-2"
        >
          <ArrowLeft aria-hidden className="size-4" />
          Back
        </ButtonLink>
      )}
      <nav aria-label="Breadcrumb" className="min-w-0">
        <ol className="flex flex-wrap items-center gap-x-1.5 gap-y-1 text-sm">
          {trail.map((crumb, index) => {
            const isCurrent = index === trail.length - 1;
            return (
              <li
                key={`${index}-${crumb.label}`}
                className="flex min-w-0 items-center gap-1.5"
              >
                {index > 0 && (
                  <ChevronRight
                    aria-hidden
                    className="size-3.5 shrink-0 text-fg-tertiary"
                  />
                )}
                {crumb.href && !isCurrent ? (
                  <Link
                    href={crumb.href}
                    className="max-w-48 truncate text-fg-secondary underline-offset-2 hover:text-foreground hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
                  >
                    {crumb.label}
                  </Link>
                ) : (
                  <span
                    aria-current={isCurrent ? "page" : undefined}
                    className="max-w-64 truncate font-medium"
                  >
                    {crumb.label}
                  </span>
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
}
