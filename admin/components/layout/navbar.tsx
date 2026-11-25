"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Avatar from "@/components/common/avatar";
import Button from "@/components/common/button";
import StatusBadge from "@/components/common/status-badge";
import NotificationBell from "@/components/notifications/notification-bell";
import { audienceFor } from "@/constants/audience";
import { NotificationsRoute } from "@/constants/notifications";
import { Route } from "@/constants/web-routes";
import { useAtomValue } from "jotai";
import { Menu } from "lucide-react";
import Link from "next/link";

type NavbarProp = Readonly<{ title?: string; onOpenMenu: () => void }>;

export default function Navbar({ title, onOpenMenu }: NavbarProp) {
  const user = useAtomValue(UserAtom);
  const audience = user && audienceFor(user);

  return (
    <header className="flex h-16 shrink-0 items-center gap-3 border-b border-default bg-background px-4 md:px-8">
      <Button
        variant="secondary"
        onClick={onOpenMenu}
        size="sm"
        className="gap-2 md:hidden"
      >
        <Menu aria-hidden className="size-4" />
        <span className="max-sm:sr-only">Menu</span>
      </Button>
      {title && (
        <p className="min-w-0 truncate text-heading">{title}</p>
      )}
      <div className="ml-auto flex items-center gap-3">
        {audience && audience !== "admin" && (
          <NotificationBell href={NotificationsRoute[audience]} />
        )}
        {user?.mfa_status === "VERIFIED" && (
          <StatusBadge tone="success" className="hidden sm:inline-flex">
            MFA verified
          </StatusBadge>
        )}
        {user && (
          <Link
            href={Route.account}
            aria-label="Your account"
            title={`${user.first_name} ${user.last_name}`}
            className="rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border"
          >
            <Avatar firstName={user.first_name} lastName={user.last_name} />
          </Link>
        )}
      </div>
    </header>
  );
}
