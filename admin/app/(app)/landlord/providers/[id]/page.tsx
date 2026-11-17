import ProviderEditorPage from "@/components/providers/provider-editor";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Edit tradesperson · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/landlord/providers/[id]">>) {
  return <ProviderEditorPage params={params} />;
}
