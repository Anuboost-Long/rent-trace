import UnitDetailPage from "@/components/properties/unit-detail";

export default function Page({
  params,
}: PageProps<"/admin/properties/[id]/units/[unitId]">) {
  return <UnitDetailPage audience="admin" params={params} />;
}
