import TenancyDetailPage from "@/components/tenancies/tenancy-detail";

export default function Page({
  params,
}: Readonly<PageProps<"/landlord/tenancies/[id]">>) {
  return <TenancyDetailPage audience="landlord" params={params} />;
}
