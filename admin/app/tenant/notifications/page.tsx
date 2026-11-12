import NotificationListPage from "@/components/notifications/notification-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Notifications · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/tenant/notifications">>) {
  return <NotificationListPage audience="tenant" searchParams={searchParams} />;
}
