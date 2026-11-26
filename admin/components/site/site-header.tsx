import ButtonLink from "@/components/common/button-link";
import NotificationBell from "@/components/notifications/notification-bell";
import { AUDIENCE_LABEL, audienceFor, homePathFor } from "@/constants/audience";
import { NotificationsRoute } from "@/constants/notifications";
import { Route } from "@/constants/web-routes";
import { getViewer } from "@/utils/viewer";
import Link from "next/link";
import { Suspense } from "react";

import AccountMenu from "./account-menu";
import SiteNav, { type RoleLink } from "./site-nav";

export default function SiteHeader() {
  return (
    <header className="sticky top-0 z-30 border-b border-default bg-background">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
        <div className="flex items-center gap-2">
          <Link
            href={Route.home}
            className="mr-2 text-xl font-bold tracking-tight focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
          >
            RentTrace
          </Link>
          <Suspense fallback={<SiteNav roleLink={null} />}>
            <RoleNav />
          </Suspense>
        </div>
        <div className="flex items-center gap-2">
          <Suspense fallback={<div className="h-10 w-24" />}>
            <HeaderActions />
          </Suspense>
        </div>
      </div>
    </header>
  );
}

async function RoleNav() {
  const viewer = await getViewer();
  const audience = viewer && audienceFor(viewer);
  const roleLink: RoleLink = !viewer
    ? {
        href: Route.auth.sign_up,
        label: "For landlords",
        activePrefix: Route.auth.sign_up,
      }
    : audience === "landlord"
      ? {
          href: "/landlord/properties",
          label: "My properties",
          activePrefix: "/landlord",
        }
      : audience === "tenant"
        ? {
            href: "/tenant/tenancies",
            label: "My tenancies",
            activePrefix: "/tenant",
          }
        : audience === "admin"
          ? { href: "/admin", label: "Admin", activePrefix: "/admin" }
          : {
              href: Route.auth.onboarding,
              label: "Finish setting up",
              activePrefix: Route.auth.onboarding,
            };

  return <SiteNav roleLink={roleLink} />;
}

async function HeaderActions() {
  const viewer = await getViewer();

  if (!viewer) {
    return (
      <>
        <ButtonLink href={Route.auth.sign_in} variant="quiet" size="sm">
          Sign in
        </ButtonLink>
        <ButtonLink
          href={Route.auth.sign_up}
          size="sm"
          className="hidden sm:inline-flex"
        >
          Create account
        </ButtonLink>
      </>
    );
  }

  const audience = audienceFor(viewer);
  return (
    <>
      {audience && (
        <NotificationBell
          href={NotificationsRoute[audience]}
          audience={audience}
        />
      )}
      <AccountMenu
        name={`${viewer.first_name} ${viewer.last_name}`.trim()}
        email={viewer.email}
        roleLabel={audience ? AUDIENCE_LABEL[audience] : "Setting up"}
        homeHref={homePathFor(viewer)}
        homeLabel={
          audience
            ? `Go to ${AUDIENCE_LABEL[audience]} area`
            : "Finish setting up"
        }
      />
    </>
  );
}
