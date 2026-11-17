import TenancyDetailPage from "@/components/tenancies/tenancy-detail";

export default function Page({
  params,
}: Readonly<PageProps<"/admin/tenancies/[id]">>) {
  return <TenancyDetailPage audience="admin" params={params} />;
}
