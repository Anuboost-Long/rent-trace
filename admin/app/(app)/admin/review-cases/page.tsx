import PageHeader from "@/components/layout/page-header";
import ReviewCaseList from "@/components/reviews/review-case-list";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Review cases · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/review-cases">>) {
  return (
    <>
      <PageHeader
        title="Review cases"
        description="Condition reports that a landlord or tenant asked an admin to decide."
      />
      <ReviewCaseList searchParams={searchParams} />
    </>
  );
}
