import TenancyListPage from "@/components/tenancies/tenancy-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Tenancies · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/tenancies">>) {
  return <TenancyListPage audience="admin" searchParams={searchParams} />;
}
