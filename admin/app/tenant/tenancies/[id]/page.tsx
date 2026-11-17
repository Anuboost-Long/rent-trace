import MyTenancyDetailPage from "@/components/tenancies/my-tenancy-detail";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Your tenancy · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/tenant/tenancies/[id]">>) {
  return <MyTenancyDetailPage params={params} />;
}
