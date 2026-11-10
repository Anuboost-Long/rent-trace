import { handleGetMe } from "@/api/services/auth/serve-action";
import {
  audienceFor,
  isMemberOf,
  SIDEBAR_COOKIE,
  type Audience,
} from "@/constants/navigation";
import { Route } from "@/constants/web-routes";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import AppShell from "./app-shell";
import ShellSkeleton from "./shell-skeleton";

type AudienceLayoutProp = Readonly<{
  audience?: Audience;
  children: React.ReactNode;
}>;

export default function AudienceLayout(props: AudienceLayoutProp) {
  return (
    <Suspense fallback={<ShellSkeleton />}>
      <SignedInShell {...props} />
    </Suspense>
  );
}

async function SignedInShell({ audience, children }: AudienceLayoutProp) {
  const { data: user } = await handleGetMe();
  const target = user && (audience ?? audienceFor(user));
  if (!user || !target || !isMemberOf(target, user)) redirect(Route.home);
  if (user.mfa_status === "ENROL" || user.mfa_status === "VERIFY") {
    redirect(Route.auth.mfa);
  }

  const sidebarCollapsed = (await cookies()).get(SIDEBAR_COOKIE)?.value === "1";

  return (
    <AppShell audience={target} user={user} sidebarCollapsed={sidebarCollapsed}>
      {children}
    </AppShell>
  );
}
