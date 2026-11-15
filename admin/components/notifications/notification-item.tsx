"use client";
import { handleMarkNotificationRead } from "@/api/services/notifications/serve-action";
import LocalTime from "@/components/common/local-time";
import type { AppNotification } from "@/types/notifications/models";
import clsx from "clsx";
import Link from "next/link";
import { useRouter } from "next/navigation";

type NotificationItemProp = Readonly<{
  notification: AppNotification;
  href: string | null;
}>;

const rowClassName = clsx(
  "flex w-full items-start gap-3 p-4 text-left",
  "hover:bg-foreground/5 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground",
);

export default function NotificationItem({
  notification,
  href,
}: NotificationItemProp) {
  const router = useRouter();
  const isUnread = notification.read_at === null;

  const markRead = async () => {
    if (!isUnread) return;
    await handleMarkNotificationRead(notification.id);
    if (!href) router.refresh();
  };

  const content = (
    <>
      <span
        aria-hidden
        className={clsx(
          "mt-2 size-2 shrink-0 rounded-full",
          isUnread ? "bg-foreground" : "bg-transparent",
        )}
      />
      <span className="min-w-0 flex-1">
        <span
          className={clsx("block", isUnread ? "font-semibold" : "font-medium")}
        >
          {notification.title}
          {isUnread && <span className="sr-only"> (unread)</span>}
        </span>
        <span className="mt-0.5 block text-sm text-foreground/70">
          {notification.body}
        </span>
        <span className="mt-1 block text-xs text-foreground/60">
          <LocalTime iso={notification.created_at} withTime />
        </span>
      </span>
    </>
  );

  return href ? (
    <Link href={href} onClick={markRead} className={rowClassName}>
      {content}
    </Link>
  ) : (
    <button type="button" onClick={markRead} className={rowClassName}>
      {content}
    </button>
  );
}
