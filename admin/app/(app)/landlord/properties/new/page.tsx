import NewPropertyPage from "@/components/properties/new-property";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "New property · RentTrace" };

export default function Page() {
  return <NewPropertyPage audience="landlord" />;
}
