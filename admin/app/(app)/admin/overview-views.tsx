"use client";
import { Route } from "@/constants/web-routes";
import clsx from "clsx";
import { useState } from "react";

const VIEWS = [
  { value: "menu", label: "Menu", href: Route.admin.index },
  {
    value: "dashboard",
    label: "Dashboard",
    href: `${Route.admin.index}?view=dashboard`,
  },
] as const;

export type OverviewView = (typeof VIEWS)[number]["value"];

type OverviewViewsProp = Readonly<{
  initialView: OverviewView;
  menu: React.ReactNode;
  dashboard: React.ReactNode;
}>;

export default function OverviewViews({
  initialView,
  menu,
  dashboard,
}: OverviewViewsProp) {
  const [view, setView] = useState(initialView);
  const activeIndex = VIEWS.findIndex((tab) => tab.value === view);

  const select = (tab: (typeof VIEWS)[number]) => {
    setView(tab.value);
    window.history.replaceState(null, "", tab.href);
  };

  return (
    <>
      <div
        role="tablist"
        aria-label="Overview views"
        className="relative mb-6 flex border-b border-default"
      >
        {VIEWS.map((tab) => (
          <button
            key={tab.value}
            id={`overview-tab-${tab.value}`}
            type="button"
            role="tab"
            aria-selected={tab.value === view}
            aria-controls="overview-panel"
            onClick={() => select(tab)}
            className={clsx(
              "w-28 py-2.5 text-sm transition-colors motion-reduce:transition-none",
              "focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-border",
              tab.value === view
                ? "font-semibold"
                : "text-fg-secondary hover:text-foreground",
            )}
          >
            {tab.label}
          </button>
        ))}
        <span
          aria-hidden
          style={{ translate: `${activeIndex * 100}% 0` }}
          className="absolute bottom-0 left-0 h-0.5 w-28 bg-brand transition-[translate] duration-200 ease-out motion-reduce:transition-none"
        />
      </div>
      <div
        key={view}
        id="overview-panel"
        role="tabpanel"
        aria-labelledby={`overview-tab-${view}`}
        className="animate-panel-in motion-reduce:animate-none"
      >
        {view === "dashboard" ? dashboard : menu}
      </div>
    </>
  );
}
