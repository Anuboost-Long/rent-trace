import ProviderListPage from "@/components/providers/provider-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Tradespeople · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/landlord/providers">>) {
  return <ProviderListPage searchParams={searchParams} />;
}
