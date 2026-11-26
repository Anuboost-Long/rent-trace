import BrandLogo from "@/components/common/brand-logo";
import { audienceFor, homePathFor } from "@/constants/audience";
import { Route } from "@/constants/web-routes";
import { getViewer } from "@/utils/viewer";
import Link from "next/link";
import { Suspense } from "react";

const linkClassName =
  "text-sm text-fg-secondary hover:text-foreground hover:underline underline-offset-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border";

export default function SiteFooter() {
  return (
    <footer className="mt-24 border-t border-default">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-10 sm:px-6 md:flex-row md:justify-between">
        <div className="max-w-xs">
          <BrandLogo
            variant="wordmark"
            tone="light"
            alt="RentTrace"
            className="h-7 w-auto"
          />
          <p className="mt-2 text-sm text-fg-secondary">
            Rentals and rent records for tenants and landlords.
          </p>
        </div>
        <nav aria-label="Footer" className="flex gap-12">
          <ul className="space-y-2">
            <li>
              <Link href={Route.listings} className={linkClassName}>
                Browse rentals
              </Link>
            </li>
          </ul>
          <Suspense fallback={null}>
            <AccountLinks />
          </Suspense>
        </nav>
      </div>
    </footer>
  );
}

async function AccountLinks() {
  const viewer = await getViewer();
  const isLandlord = viewer && audienceFor(viewer) === "landlord";

  return (
    <ul className="space-y-2">
      {!viewer && (
        <>
          <li>
            <Link href={Route.auth.sign_up} className={linkClassName}>
              For landlords
            </Link>
          </li>
          <li>
            <Link href={Route.auth.sign_in} className={linkClassName}>
              Sign in
            </Link>
          </li>
          <li>
            <Link href={Route.auth.sign_up} className={linkClassName}>
              Create account
            </Link>
          </li>
        </>
      )}
      {viewer && (
        <>
          {isLandlord && (
            <li>
              <Link href="/landlord/properties" className={linkClassName}>
                My properties
              </Link>
            </li>
          )}
          <li>
            <Link href={homePathFor(viewer)} className={linkClassName}>
              Your area
            </Link>
          </li>
          <li>
            <Link href={Route.account} className={linkClassName}>
              Account settings
            </Link>
          </li>
        </>
      )}
    </ul>
  );
}
