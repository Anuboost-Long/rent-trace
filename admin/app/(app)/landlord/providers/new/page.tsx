import ProviderEditorPage from "@/components/providers/provider-editor";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Add tradesperson · RentTrace" };

export default function Page() {
  return <ProviderEditorPage />;
}
