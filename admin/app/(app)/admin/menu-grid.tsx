"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import { groupNavItems, Navigation } from "@/constants/navigation";
import { Route } from "@/constants/web-routes";
import { useAtomValue } from "jotai";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const apps = Navigation.admin.items.filter(
  (item) => item.href !== Route.admin.index,
);

const STAGGER_MS = 60;

const followPointer = (event: React.PointerEvent<HTMLDivElement>) => {
  const box = event.currentTarget.getBoundingClientRect();
  event.currentTarget.style.setProperty("--x", `${event.clientX - box.left}px`);
  event.currentTarget.style.setProperty("--y", `${event.clientY - box.top}px`);
};

export default function MenuGrid() {
  const me = useAtomValue(UserAtom);
  const [query, setQuery] = useState("");
  const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
  const groups = groupNavItems(
    apps
      .filter(
        (app) => !app.permission || me?.permissions.includes(app.permission),
      )
      .filter((app) =>
        terms.every((term) =>
          `${app.label} ${app.description ?? ""}`.toLowerCase().includes(term),
        ),
      ),
  );

  return (
    <div className="space-y-10">
      <TextInput
        label="Find a module"
        name="module-search"
        type="search"
        autoComplete="off"
        placeholder="Users, bans, properties…"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        className="max-w-sm"
      />
      {groups.length === 0 && (
        <div role="status" className="flex flex-col items-start gap-3">
          <p className="text-foreground/70">
            No modules match &ldquo;{query}&rdquo;.
          </p>
          <Button variant="quiet" size="sm" onClick={() => setQuery("")}>
            Clear search
          </Button>
        </div>
      )}
      {groups.map(([group, items], groupIndex) => (
        <section
          key={group}
          aria-labelledby={`group-${group}`}
          style={{
            animationDelay: `${groupIndex * STAGGER_MS}ms`,
            animationFillMode: "backwards",
          }}
          className="animate-panel-in grid gap-4 lg:grid-cols-[12rem_1fr] lg:gap-8 motion-reduce:animate-none"
        >
          <div>
            <h2 id={`group-${group}`} className="text-sm font-semibold">
              {group || "Other"}
            </h2>
            <p className="mt-0.5 text-sm text-foreground/60">
              {items.length} {items.length === 1 ? "module" : "modules"}
            </p>
          </div>
          <div
            onPointerMove={followPointer}
            className="group/list relative overflow-hidden rounded-2xl border border-foreground/15"
          >
            <div
              aria-hidden
              style={{
                background:
                  "radial-gradient(280px circle at var(--x, 50%) var(--y, 50%), color-mix(in srgb, currentColor 7%, transparent), transparent 70%)",
              }}
              className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover/list:opacity-100 motion-reduce:hidden"
            />
            <ul className="relative divide-y divide-foreground/15">
              {items.map((app) => (
                <li key={app.href}>
                  <Link
                    href={app.href}
                    className="group/row flex items-center gap-4 px-4 py-4 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground"
                  >
                    <span className="flex size-11 shrink-0 items-center justify-center rounded-lg border border-foreground/15 bg-background">
                      <app.icon
                        aria-hidden
                        className="size-5"
                        strokeWidth={1.5}
                      />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block font-medium">{app.label}</span>
                      {app.description && (
                        <span className="block text-sm text-foreground/70">
                          {app.description}
                        </span>
                      )}
                    </span>
                    <ArrowRight
                      aria-hidden
                      className="size-4 shrink-0 -translate-x-1 opacity-0 transition group-hover/row:translate-x-0 group-hover/row:opacity-100 group-focus-visible/row:translate-x-0 group-focus-visible/row:opacity-100 motion-reduce:transition-none"
                    />
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>
      ))}
    </div>
  );
}
