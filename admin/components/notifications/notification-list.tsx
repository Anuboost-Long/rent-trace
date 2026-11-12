import { handleGetNotifications } from "@/api/services/notifications/serve-action";
import Pagination from "@/components/common/table/pagination";
import ContentSkeleton from "@/components/layout/content-skeleton";
import type { Audience } from "@/constants/audience";
import {
  notificationHref,
  NotificationsRoute,
} from "@/constants/notifications";
import clsx from "clsx";
import Link from "next/link";
import { Suspense } from "react";

import MarkAllReadButton from "./mark-all-read-button";
import NotificationItem from "./notification-item";

type SearchParams = Promise<Record<string, string | string[] | undefined>>;

type NotificationListProp = Readonly<{
  audience: Audience;
  searchParams: SearchParams;
}>;

const tabClassName = (active: boolean) =>
  clsx(
    "flex h-9 items-center rounded-lg px-3 text-sm",
    active ? "bg-foreground/10 font-semibold" : "text-foreground/70",
    "hover:bg-foreground/5 focus-visible:outline-2 focus-visible:outline-foreground",
  );

export default function NotificationListPage({
  audience,
  searchParams,
}: NotificationListProp) {
  return (
    <Suspense fallback={<ContentSkeleton />}>
      <NotificationList audience={audience} searchParams={searchParams} />
    </Suspense>
  );
}

async function NotificationList({
  audience,
  searchParams,
}: NotificationListProp) {
  const query = await searchParams;
  const unreadOnly = query.unread === "true";
  const page = Number(typeof query.page === "string" ? query.page : 1) || 1;
  const { data, error } = await handleGetNotifications({
    ...(unreadOnly && { unread: "true" as const }),
    page,
  });
  const base = NotificationsRoute[audience];
  const hasUnread = !error && data.results.some((item) => !item.read_at);

  const hrefForPage = (target: number) => {
    const params = new URLSearchParams({ page: String(target) });
    if (unreadOnly) params.set("unread", "true");
    return `${base}?${params}`;
  };

  return (
    <>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Notifications</h1>
          <p className="mt-1 text-foreground/70">
            Requests and updates that need your attention.
          </p>
        </div>
        <MarkAllReadButton disabled={!hasUnread} />
      </div>
      <nav aria-label="Filter notifications" className="mb-4 flex gap-1">
        <Link
          href={base}
          aria-current={unreadOnly ? undefined : "page"}
          className={tabClassName(!unreadOnly)}
        >
          All
        </Link>
        <Link
          href={`${base}?unread=true`}
          aria-current={unreadOnly ? "page" : undefined}
          className={tabClassName(unreadOnly)}
        >
          Unread
        </Link>
      </nav>
      {error ? (
        <p role="alert" className="text-red-600">
          {error.message}
        </p>
      ) : data.results.length === 0 ? (
        <div className="py-12 text-center">
          <p className="font-medium">
            {unreadOnly ? "You're all caught up" : "No notifications yet"}
          </p>
          <p className="mt-1 text-sm text-foreground/70">
            Updates about your requests and invitations show up here.
          </p>
        </div>
      ) : (
        <>
          <ul className="divide-y divide-foreground/15 overflow-hidden rounded-xl border border-foreground/15">
            {data.results.map((item) => (
              <li key={item.id}>
                <NotificationItem
                  notification={item}
                  href={notificationHref(item.kind, item.subject_id, audience)}
                />
              </li>
            ))}
          </ul>
          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            count={data.count}
            hrefForPage={hrefForPage}
          />
        </>
      )}
    </>
  );
}
