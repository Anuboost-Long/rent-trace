import type { Metadata } from "next";
import { Suspense } from "react";

import ConfirmEmail from "./confirm-email";

export const metadata: Metadata = {
  title: "Verify your email · RentTrace",
  referrer: "no-referrer",
  robots: { index: false },
};

export default function VerifyEmailPage({
  searchParams,
}: PageProps<"/verify-email">) {
  return (
    <Suspense>
      <TokenConfirm searchParams={searchParams} />
    </Suspense>
  );
}

async function TokenConfirm({
  searchParams,
}: Readonly<Pick<PageProps<"/verify-email">, "searchParams">>) {
  const { token } = await searchParams;
  return <ConfirmEmail token={typeof token === "string" ? token : ""} />;
}
