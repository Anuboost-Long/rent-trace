import TenancyListPage from "@/components/tenancies/tenancy-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Tenancies · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/landlord/tenancies">>) {
  return <TenancyListPage audience="landlord" searchParams={searchParams} />;
}
