"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { handleSignOut } from "@/api/services/auth/serve-action";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import NotificationBell from "@/components/notifications/notification-bell";
import { audienceFor } from "@/constants/audience";
import { NotificationsRoute } from "@/constants/notifications";
import { Route } from "@/constants/web-routes";
import { useAtomValue } from "jotai";
import { LogOut, Menu, UserRound } from "lucide-react";

type NavbarProp = Readonly<{ onOpenMenu: () => void }>;

export default function Navbar({ onOpenMenu }: NavbarProp) {
  const user = useAtomValue(UserAtom);
  const audience = user && audienceFor(user);

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-foreground/15 px-4">
      <Button
        variant="quiet"
        onClick={onOpenMenu}
        size="sm"
        className="gap-2 md:hidden"
      >
        <Menu aria-hidden className="size-4" />
        Menu
      </Button>
      <div className="ml-auto flex items-center gap-4">
        {audience && <NotificationBell href={NotificationsRoute[audience]} />}
        {user && (
          <ButtonLink
            href={Route.account}
            variant="quiet"
            size="sm"
            aria-label="Your account"
            className="gap-2"
          >
            <UserRound aria-hidden className="size-4" />
            <span className="hidden sm:inline">
              {user.first_name} {user.last_name}
            </span>
          </ButtonLink>
        )}
        <form action={handleSignOut}>
          <Button type="submit" variant="quiet" size="sm" className="gap-2">
            <LogOut aria-hidden className="size-4" />
            Sign out
          </Button>
        </form>
      </div>
    </header>
  );
}
