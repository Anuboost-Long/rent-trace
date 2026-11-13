import PropertyListPage from "@/components/properties/property-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Properties · RentTrace" };

export default function Page({ searchParams }: PageProps<"/admin/properties">) {
  return <PropertyListPage audience="admin" searchParams={searchParams} />;
}
