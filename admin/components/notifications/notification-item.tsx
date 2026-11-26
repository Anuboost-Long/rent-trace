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
  compact?: boolean;
  onOpen?: () => void;
}>;

const rowClassName = clsx(
  "flex w-full items-start gap-3 p-4 text-left",
  "hover:bg-subtle focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-border",
);

export default function NotificationItem({
  notification,
  href,
  compact,
  onOpen,
}: NotificationItemProp) {
  const router = useRouter();
  const isUnread = notification.read_at === null;

  const markRead = async () => {
    onOpen?.();
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
          isUnread ? "bg-brand" : "bg-transparent",
        )}
      />
      <span className="min-w-0 flex-1">
        <span
          className={clsx("block", isUnread ? "font-semibold" : "font-medium")}
        >
          {notification.title}
          {isUnread && <span className="sr-only"> (unread)</span>}
        </span>
        <span
          className={clsx(
            "mt-0.5 block text-sm text-fg-secondary",
            compact && "line-clamp-2",
          )}
        >
          {notification.body}
        </span>
        <span className="mt-1 block text-xs text-fg-tertiary">
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
