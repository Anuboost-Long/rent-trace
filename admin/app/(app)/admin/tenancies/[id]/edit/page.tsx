import EditTenancyPage from "@/components/tenancies/edit-tenancy";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Edit tenancy · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/admin/tenancies/[id]/edit">>) {
  return <EditTenancyPage audience="admin" params={params} />;
}
