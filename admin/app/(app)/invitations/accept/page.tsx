import type { Metadata } from "next";

import AcceptInvitation from "./accept-invitation";

export const metadata: Metadata = { title: "Join a tenancy · RentTrace" };

export default async function Page({
  searchParams,
}: Readonly<PageProps<"/invitations/accept">>) {
  const { token } = await searchParams;

  return (
    <div className="max-w-md">
      <h1 className="text-2xl font-semibold">Join a tenancy</h1>
      {typeof token === "string" && token !== "" ? (
        <AcceptInvitation token={token} />
      ) : (
        <p role="alert" className="mt-4 text-red-600">
          This link is missing its invitation. Open the link from your email
          again.
        </p>
      )}
    </div>
  );
}
