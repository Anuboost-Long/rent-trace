import { handleGetMe } from "@/api/services/auth/serve-action";
import PageHeader from "@/components/layout/page-header";
import { FormSkeleton } from "@/components/layout/page-skeletons";
import { formatDate } from "@/utils/format-date";
import type { Metadata } from "next";
import { Suspense } from "react";

import ProfileSection from "./profile-section";
import SecuritySection from "./security-section";

export const metadata: Metadata = { title: "Account · RentTrace" };

export default function AccountPage() {
  return (
    <div className="max-w-2xl">
      <PageHeader
        title="Account"
        description="Your details and how you sign in."
      />
      <Suspense fallback={<FormSkeleton />}>
        <Account />
      </Suspense>
    </div>
  );
}

async function Account() {
  const { data: user, error } = await handleGetMe();
  if (error) {
    return (
      <p role="alert" className="text-red-600">
        {error.message}
      </p>
    );
  }

  const details: [string, string][] = [
    ["Email", user.email],
    ["Role", user.role_names.join(", ") || "None yet"],
    [
      "Sign-in method",
      user.auth_method === "GOOGLE" ? "Google" : "Email and password",
    ],
    ["Email verified", formatDate(user.email_verified_at)],
    ["Member since", formatDate(user.created_at)],
    ["Last sign-in", formatDate(user.last_login_at)],
  ];

  return (
    <div className="flex flex-col gap-10">
      <ProfileSection user={user} />
      <section aria-labelledby="details-heading">
        <h2 id="details-heading" className="text-lg font-semibold">
          Account details
        </h2>
        <dl className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
          {details.map(([label, value]) => (
            <div
              key={label}
              className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]"
            >
              <dt className="text-sm text-foreground/70">{label}</dt>
              <dd className="break-words">{value}</dd>
            </div>
          ))}
        </dl>
      </section>
      <SecuritySection user={user} />
    </div>
  );
}
