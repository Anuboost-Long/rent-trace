import EditPropertyPage from "@/components/properties/edit-property";

export default function Page({
  params,
}: PageProps<"/landlord/properties/[id]/edit">) {
  return <EditPropertyPage audience="landlord" params={params} />;
}
