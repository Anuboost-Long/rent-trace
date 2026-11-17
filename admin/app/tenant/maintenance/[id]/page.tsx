import IssueDetailPage from "@/components/maintenance/issue-detail";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Maintenance issue · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/tenant/maintenance/[id]">>) {
  return <IssueDetailPage audience="tenant" params={params} />;
}
