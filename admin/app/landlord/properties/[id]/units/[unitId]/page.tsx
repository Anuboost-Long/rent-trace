import UnitDetailPage from "@/components/properties/unit-detail";

export default function Page({
  params,
}: PageProps<"/landlord/properties/[id]/units/[unitId]">) {
  return <UnitDetailPage audience="landlord" params={params} />;
}
