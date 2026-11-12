"use client";
import { handleGetUnreadCount } from "@/api/services/notifications/serve-action";
import clsx from "clsx";
import { Bell } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const POLL_MS = 60_000;

export default function NotificationBell({ href }: Readonly<{ href: string }>) {
  const pathname = usePathname();
  const [unread, setUnread] = useState(0);

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

  return (
    <Link
      href={href}
      aria-label={
        unread > 0 ? `Notifications, ${unread} unread` : "Notifications"
      }
      className={clsx(
        "relative grid size-10 place-items-center rounded-lg",
        "hover:bg-foreground/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-foreground",
      )}
    >
      <Bell aria-hidden className="size-5" />
      {unread > 0 && (
        <span
          aria-hidden
          className="absolute top-1 right-1 grid min-w-4 place-items-center rounded-full bg-foreground px-1 text-[10px] leading-4 font-semibold text-background tabular-nums"
        >
          {unread > 99 ? "99+" : unread}
        </span>
      )}
    </Link>
  );
}
