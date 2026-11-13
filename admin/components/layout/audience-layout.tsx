import { audienceFor, SIDEBAR_COOKIE } from "@/constants/navigation";
import { Route } from "@/constants/web-routes";
import { getMe } from "@/utils/viewer";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import AppShell from "./app-shell";
import ShellSkeleton from "./shell-skeleton";

type AudienceLayoutProp = Readonly<{ children: React.ReactNode }>;

export default function AudienceLayout(props: AudienceLayoutProp) {
  return (
    <Suspense fallback={<ShellSkeleton />}>
      <SignedInShell {...props} />
    </Suspense>
  );
}

async function SignedInShell({ children }: AudienceLayoutProp) {
  const { data: user } = await getMe();
  const home = user && audienceFor(user);
  if (!user || !home) redirect(Route.home);
  if (user.mfa_status === "ENROL" || user.mfa_status === "VERIFY") {
    redirect(Route.auth.mfa);
  }

  const sidebarCollapsed = (await cookies()).get(SIDEBAR_COOKIE)?.value === "1";

  return (
    <AppShell home={home} user={user} sidebarCollapsed={sidebarCollapsed}>
      {children}
    </AppShell>
  );
}
