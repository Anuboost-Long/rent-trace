import EditPropertyPage from "@/components/properties/edit-property";

export default function Page({
  params,
}: PageProps<"/admin/properties/[id]/edit">) {
  return <EditPropertyPage audience="admin" params={params} />;
}
