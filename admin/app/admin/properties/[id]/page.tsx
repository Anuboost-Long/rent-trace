import PropertyDetailPage from "@/components/properties/property-detail";

export default function Page({ params }: PageProps<"/admin/properties/[id]">) {
  return <PropertyDetailPage audience="admin" params={params} />;
}
