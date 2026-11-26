"use client";
import {
  handleGetNotifications,
  handleGetUnreadCount,
} from "@/api/services/notifications/serve-action";
import Spinner from "@/components/common/loading/spinner";
import type { Audience } from "@/constants/audience";
import { notificationHref } from "@/constants/notifications";
import type { AppNotification } from "@/types/notifications/models";
import clsx from "clsx";
import { Bell } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";

import NotificationItem from "./notification-item";

const POLL_MS = 60_000;
const PREVIEW_COUNT = 5;

type NotificationBellProp = Readonly<{ href: string; audience: Audience }>;

export default function NotificationBell({
  href,
  audience,
}: NotificationBellProp) {
  const pathname = usePathname();
  const rootRef = useRef<HTMLDivElement>(null);
  const [unread, setUnread] = useState(0);
  const [open, setOpen] = useState(false);
  const [recent, setRecent] = useState<AppNotification[] | null>(null);

  useEffect(() => {
    let active = true;
    const refresh = async () => {
      if (document.hidden) return;
      const count = await handleGetUnreadCount();
      if (active && count !== null) setUnread(count);
    };
    refresh();
    const timer = setInterval(refresh, POLL_MS);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      active = false;
      clearInterval(timer);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, [pathname]);

  useEffect(() => {
    if (!open) return;
    let active = true;
    handleGetNotifications({ page: 1 }).then(({ data }) => {
      if (active) setRecent(data ? data.results.slice(0, PREVIEW_COUNT) : []);
    });
    const close = (event: PointerEvent | KeyboardEvent) => {
      const outside =
        event instanceof PointerEvent &&
        !rootRef.current?.contains(event.target as Node);
      const escaped = event instanceof KeyboardEvent && event.key === "Escape";
      if (outside || escaped) setOpen(false);
    };
    document.addEventListener("pointerdown", close);
    document.addEventListener("keydown", close);
    return () => {
      active = false;
      document.removeEventListener("pointerdown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open]);

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        aria-haspopup="true"
        aria-expanded={open}
        aria-label={
          unread > 0 ? `Notifications, ${unread} unread` : "Notifications"
        }
        onClick={() => setOpen((value) => !value)}
        className={clsx(
          "relative grid size-10 place-items-center rounded-lg",
          open && "bg-subtle",
          "hover:bg-subtle focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border",
        )}
      >
        <Bell aria-hidden className="size-5" />
        {unread > 0 && (
          <span
            aria-hidden
            className="absolute top-1 right-1 grid min-w-4 place-items-center rounded-full bg-brand px-1 text-[10px] leading-4 font-semibold text-on-brand tabular-nums"
          >
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </button>
      {open && (
        <div
          role="region"
          aria-label="Recent notifications"
          className="absolute right-0 z-40 mt-2 w-88 max-w-[calc(100vw-2rem)] animate-panel-in overflow-hidden rounded-xl border border-default bg-background shadow-medium motion-reduce:animate-none"
        >
          <div className="flex items-center justify-between border-b border-default px-4 py-3">
            <p className="text-body-sm font-semibold">Notifications</p>
            {unread > 0 && (
              <p className="text-caption text-fg-tertiary">{unread} unread</p>
            )}
          </div>
          {recent === null ? (
            <div className="grid h-24 place-items-center">
              <Spinner />
            </div>
          ) : recent.length === 0 ? (
            <p className="px-4 py-8 text-center text-body-sm text-fg-secondary">
              You&apos;re all caught up.
            </p>
          ) : (
            <ul className="max-h-96 divide-y divide-default overflow-y-auto">
              {recent.map((item) => (
                <li key={item.id}>
                  <NotificationItem
                    notification={item}
                    href={notificationHref(
                      item.kind,
                      item.subject_id,
                      audience,
                    )}
                    compact
                    onOpen={() => setOpen(false)}
                  />
                </li>
              ))}
            </ul>
          )}
          <Link
            href={href}
            onClick={() => setOpen(false)}
            className="block border-t border-default px-4 py-3 text-center text-body-sm font-semibold text-fg-brand hover:bg-subtle focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-border"
          >
            See all
          </Link>
        </div>
      )}
    </div>
  );
}
