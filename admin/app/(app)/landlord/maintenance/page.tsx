import PageHeader from "@/components/layout/page-header";
import IssueListBody from "@/components/maintenance/issue-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Maintenance · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/landlord/maintenance">>) {
  return (
    <>
      <PageHeader
        title="Maintenance"
        description="Issues your tenants have reported on your properties."
      />
      <IssueListBody audience="landlord" searchParams={searchParams} />
    </>
  );
}
