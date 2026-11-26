"use client";
import { handleSignOut } from "@/api/services/auth/serve-action";
import { Route } from "@/constants/web-routes";
import { ChevronDown, LogOut, UserRound } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef } from "react";

type AccountMenuProp = Readonly<{
  name: string;
  email: string;
  roleLabel: string;
  homeHref: string;
  homeLabel: string;
}>;

const itemClassName =
  "flex h-10 w-full items-center gap-2 rounded-lg px-3 text-sm hover:bg-subtle focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-brand-border";

export default function AccountMenu({
  name,
  email,
  roleLabel,
  homeHref,
  homeLabel,
}: AccountMenuProp) {
  const menuRef = useRef<HTMLDetailsElement>(null);

  useEffect(() => {
    const close = (event: PointerEvent | KeyboardEvent) => {
      const menu = menuRef.current;
      if (!menu?.open) return;
      const outside =
        event instanceof PointerEvent && !menu.contains(event.target as Node);
      const escaped = event instanceof KeyboardEvent && event.key === "Escape";
      if (outside || escaped) menu.open = false;
    };
    document.addEventListener("pointerdown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("pointerdown", close);
      document.removeEventListener("keydown", close);
    };
  }, []);

  return (
    <details ref={menuRef} className="group relative">
      <summary className="flex h-10 cursor-pointer list-none items-center gap-2 rounded-lg border border-default pr-2 pl-1.5 hover:bg-subtle focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border">
        <span
          aria-hidden
          className="flex size-7 items-center justify-center rounded-md bg-brand text-sm font-semibold text-on-brand"
        >
          {name.charAt(0).toUpperCase()}
        </span>
        <span className="hidden max-w-32 truncate text-sm font-medium sm:inline">
          {name}
        </span>
        <ChevronDown
          aria-hidden
          className="size-4 transition-transform group-open:rotate-180 motion-reduce:transition-none"
        />
        <span className="sr-only">Account menu</span>
      </summary>
      <div className="absolute right-0 z-40 mt-2 w-64 animate-panel-in rounded-xl border border-default bg-background p-2 motion-reduce:animate-none">
        <div className="border-b border-default px-3 pt-1 pb-3">
          <p className="truncate font-medium">{name}</p>
          <p className="truncate text-sm text-fg-secondary">{email}</p>
          <p className="mt-1 text-xs text-fg-tertiary">{roleLabel}</p>
        </div>
        <div className="mt-2 flex flex-col">
          <Link href={homeHref} className={itemClassName}>
            <UserRound aria-hidden className="size-4" />
            {homeLabel}
          </Link>
          <Link href={Route.account} className={itemClassName}>
            Account settings
          </Link>
          <form action={handleSignOut}>
            <button type="submit" className={itemClassName}>
              <LogOut aria-hidden className="size-4" />
              Sign out
            </button>
          </form>
        </div>
      </div>
    </details>
  );
}
