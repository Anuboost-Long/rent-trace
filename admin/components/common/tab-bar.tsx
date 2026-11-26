"use client";
import clsx from "clsx";
import Link from "next/link";
import { useLayoutEffect, useRef, useState } from "react";

export type Tab = Readonly<{
  href: string;
  label: string;
  active: boolean;
  className?: string;
}>;

type TabBarProp = Readonly<{
  label: string;
  tabs: readonly Tab[];
  className?: string;
  listClassName?: string;
  tabClassName?: string;
}>;

type Underline = { left: number; width: number };

export default function TabBar({
  label,
  tabs,
  className,
  listClassName,
  tabClassName = "h-12",
}: TabBarProp) {
  const listRef = useRef<HTMLUListElement>(null);
  const [underline, setUnderline] = useState<Underline | null>(null);
  const activeHref = tabs.find((tab) => tab.active)?.href;

  useLayoutEffect(() => {
    const list = listRef.current;
    if (!list) return;
    const measure = () => {
      const current = list.querySelector<HTMLElement>("[aria-current='page']");
      setUnderline(
        current
          ? { left: current.offsetLeft, width: current.offsetWidth }
          : null,
      );
    };
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(list);
    return () => observer.disconnect();
  }, [activeHref]);

  return (
    <nav aria-label={label} className={className}>
      <ul
        ref={listRef}
        className={clsx("relative flex gap-1 overflow-x-auto", listClassName)}
      >
        {tabs.map((tab) => (
          <li key={tab.href} className={clsx("flex", tab.className)}>
            <Link
              href={tab.href}
              aria-current={tab.active ? "page" : undefined}
              className={clsx(
                "flex items-center px-3 text-sm whitespace-nowrap",
                tabClassName,
                "transition-colors duration-200 motion-reduce:transition-none",
                "focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-border",
                tab.active
                  ? "font-semibold text-fg-brand"
                  : "text-fg-secondary hover:text-foreground",
              )}
            >
              {tab.label}
            </Link>
          </li>
        ))}
        {underline && (
          <span
            aria-hidden
            className={clsx(
              "pointer-events-none absolute bottom-0 left-0 h-0.5 bg-brand-border",
              "transition-[translate,width] duration-300 ease-out motion-reduce:transition-none",
            )}
            style={{
              width: underline.width,
              translate: `${underline.left}px`,
            }}
          />
        )}
      </ul>
    </nav>
  );
}
