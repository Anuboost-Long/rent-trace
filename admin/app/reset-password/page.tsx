import { handleGetResetPreview } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import { Route } from "@/constants/web-routes";
import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import ResetPasswordForm from "./reset-password-form";

export const metadata: Metadata = {
  title: "Choose a new password · RentTrace",
  referrer: "no-referrer",
  robots: { index: false },
};

export default function ResetPasswordPage({
  searchParams,
}: PageProps<"/reset-password">) {
  return (
    <Suspense>
      <Checked searchParams={searchParams} />
    </Suspense>
  );
}

async function Checked({
  searchParams,
}: Readonly<Pick<PageProps<"/reset-password">, "searchParams">>) {
  const { token } = await searchParams;
  const link = typeof token === "string" ? token : "";
  const { data } = link ? await handleGetResetPreview(link) : { data: null };

  if (!data) {
    return (
      <AuthCard
        heading="Link expired"
        message="This link is invalid or has expired. Ask for a new one."
      >
        <Link
          href={Route.auth.forgot_password}
          className="font-medium underline"
        >
          Send a new reset link
        </Link>
      </AuthCard>
    );
  }
  return <ResetPasswordForm token={link} requiresCode={data.requires_code} />;
}
