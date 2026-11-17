import PageHeader from "@/components/layout/page-header";
import IssueListBody from "@/components/maintenance/issue-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Maintenance · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/maintenance">>) {
  return (
    <>
      <PageHeader
        title="Maintenance"
        description="Issues reported on any property."
      />
      <IssueListBody audience="admin" searchParams={searchParams} />
    </>
  );
}
