import IssueDetailPage from "@/components/maintenance/issue-detail";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Maintenance issue · RentTrace" };

export default function Page({
  params,
}: Readonly<PageProps<"/landlord/maintenance/[id]">>) {
  return <IssueDetailPage audience="landlord" params={params} />;
}
