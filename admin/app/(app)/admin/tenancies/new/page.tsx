import NewTenancyPage from "@/components/tenancies/new-tenancy";
import type { Metadata } from "next";
import { Suspense } from "react";

export const metadata: Metadata = { title: "New tenancy · RentTrace" };

export default function Page({
  searchParams,
}: Readonly<PageProps<"/admin/tenancies/new">>) {
  return (
    <Suspense>
      <NewTenancy searchParams={searchParams} />
    </Suspense>
  );
}

async function NewTenancy({
  searchParams,
}: Readonly<Pick<PageProps<"/admin/tenancies/new">, "searchParams">>) {
  const { property } = await searchParams;
  return (
    <NewTenancyPage
      audience="admin"
      propertyId={typeof property === "string" ? property : undefined}
    />
  );
}
