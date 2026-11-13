import PropertyDetailPage from "@/components/properties/property-detail";

export default function Page({
  params,
}: PageProps<"/landlord/properties/[id]">) {
  return <PropertyDetailPage audience="landlord" params={params} />;
}
