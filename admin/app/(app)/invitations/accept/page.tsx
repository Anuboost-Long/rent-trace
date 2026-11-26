import { handlePreviewInvitation } from "@/api/services/tenancies/serve-action";
import type { Metadata } from "next";

import AcceptInvitation from "./accept-invitation";

export const metadata: Metadata = { title: "Join a tenancy · RentTrace" };

export default async function Page({
  searchParams,
}: Readonly<PageProps<"/invitations/accept">>) {
  const { token } = await searchParams;

  if (typeof token !== "string" || token === "") {
    return (
      <div className="max-w-md">
        <h1 className="text-heading">Join a tenancy</h1>
        <p role="alert" className="mt-4 text-error">
          This link is missing its invitation. Open the link from your email
          again.
        </p>
      </div>
    );
  }

  const { data: preview, error } = await handlePreviewInvitation(token);

  return (
    <div className="max-w-md">
      <h1 className="text-heading">
        {preview ? `Join ${preview.property_name}` : "Join a tenancy"}
      </h1>
      {preview && (
        <p className="mt-1 text-fg-secondary">
          {preview.unit_name} · Invited by {preview.invited_by}
        </p>
      )}
      {error ? (
        <p role="alert" className="mt-4 text-error">
          {error.message}
        </p>
      ) : (
        <AcceptInvitation token={token} />
      )}
    </div>
  );
}
