import SiteFooter from "@/components/site/site-footer";
import SiteHeader from "@/components/site/site-header";
import { isMemberOf } from "@/constants/navigation";
import { Route } from "@/constants/web-routes";
import { getViewer } from "@/utils/viewer";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import ContentSkeleton from "./content-skeleton";
import TenantNav from "./tenant-nav";
import UserProvider from "./user-provider";

const contentClassName = "mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6";

export default function TenantLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <>
      <SiteHeader />
      <Suspense
        fallback={
          <div className={contentClassName}>
            <ContentSkeleton />
          </div>
        }
      >
        <TenantArea>{children}</TenantArea>
      </Suspense>
      <SiteFooter />
    </>
  );
}

async function TenantArea({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const user = await getViewer();
  if (!user || !isMemberOf("tenant", user)) redirect(Route.home);
  if (user.mfa_status === "ENROL" || user.mfa_status === "VERIFY") {
    redirect(Route.auth.mfa);
  }

  return (
    <UserProvider user={user}>
      <TenantNav />
      <main className={contentClassName}>{children}</main>
    </UserProvider>
  );
}
