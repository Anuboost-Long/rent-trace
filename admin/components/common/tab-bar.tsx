"use client";
import clsx from "clsx";
import Link from "next/link";
import { useLayoutEffect, useRef, useState } from "react";

export type Tab = Readonly<{ href: string; label: string; active: boolean }>;

type TabBarProp = Readonly<{
  label: string;
  tabs: readonly Tab[];
  className?: string;
  listClassName?: string;
}>;

type Underline = { left: number; width: number };

export default function TabBar({
  label,
  tabs,
  className,
  listClassName,
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
          <li key={tab.href} className="flex">
            <Link
              href={tab.href}
              aria-current={tab.active ? "page" : undefined}
              className={clsx(
                "flex h-12 items-center px-3 text-sm whitespace-nowrap",
                "transition-colors duration-200 motion-reduce:transition-none",
                "focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground",
                tab.active
                  ? "font-semibold"
                  : "text-foreground/70 hover:text-foreground",
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
              "pointer-events-none absolute bottom-0 left-0 h-0.5 bg-foreground",
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
