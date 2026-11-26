"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { handleSignOut } from "@/api/services/auth/serve-action";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import {
  Navigation,
  SIDEBAR_COOKIE,
  type Audience,
} from "@/constants/navigation";
import type { Me } from "@/types/auth/models";
import clsx from "clsx";
import { createStore, Provider } from "jotai";
import { X } from "lucide-react";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState, useTransition } from "react";

import { isNavItemActive } from "./nav-link";
import Navbar from "./navbar";
import Sidebar from "./sidebar";
import SidebarToggle from "./sidebar-toggle";

type AppShellProp = Readonly<{
  home: Audience;
  user: Me;
  sidebarCollapsed: boolean;
  children: React.ReactNode;
}>;

const ONE_YEAR_SECONDS = 365 * 24 * 60 * 60;

export default function AppShell({
  home,
  user,
  sidebarCollapsed,
  children,
}: AppShellProp) {
  const [store] = useState(() => {
    const created = createStore();
    created.set(UserAtom, user);
    return created;
  });
  useEffect(() => {
    store.set(UserAtom, user);
  }, [store, user]);
  const [collapsed, setCollapsed] = useState(sidebarCollapsed);
  const [signOutOpen, setSignOutOpen] = useState(false);
  const [signingOut, startSignOut] = useTransition();
  const menuRef = useRef<HTMLDialogElement>(null);
  const pathname = usePathname();
  const section = pathname.split("/")[1];
  const audience =
    section === "admin" || section === "landlord" ? section : home;
  const tone = audience === "admin" ? "admin" : "default";
  const { label } = Navigation[audience];
  const items = Navigation[audience].items.filter(
    (item) => !item.permission || user.permissions.includes(item.permission),
  );
  const title = items
    .filter((item) => isNavItemActive(item, pathname))
    .sort((a, b) => b.href.length - a.href.length)[0]?.label;
  const closeMenu = useCallback(() => menuRef.current?.close(), []);
  const openSignOut = useCallback(() => {
    menuRef.current?.close();
    setSignOutOpen(true);
  }, []);
  const closeSignOut = useCallback(() => {
    if (!signingOut) setSignOutOpen(false);
  }, [signingOut]);

  useEffect(() => {
    const desktop = window.matchMedia("(min-width: 768px)");
    const closeOnDesktop = (event: MediaQueryListEvent) => {
      if (event.matches) closeMenu();
    };
    desktop.addEventListener("change", closeOnDesktop);
    return () => desktop.removeEventListener("change", closeOnDesktop);
  }, [closeMenu]);

  const toggleSidebar = () => {
    const next = !collapsed;
    setCollapsed(next);
    document.cookie = `${SIDEBAR_COOKIE}=${next ? 1 : 0}; path=/; max-age=${ONE_YEAR_SECONDS}; samesite=lax`;
  };

  return (
    <Provider store={store}>
      <div className="flex min-h-screen">
        <aside
          id="sidebar"
          data-collapsed={collapsed || undefined}
          className={clsx(
            "group hidden shrink-0 md:flex md:flex-col",
            "sticky top-0 h-screen",
            "w-60 data-collapsed:w-16",
            "transition-[width] duration-150 motion-reduce:transition-none",
            tone === "admin"
              ? "bg-admin text-on-brand"
              : "border-r border-default bg-background",
          )}
        >
          <Sidebar
            label={label}
            tone={tone}
            user={user}
            items={items}
            onSignOut={openSignOut}
            profileAction={
              <SidebarToggle
                collapsed={collapsed}
                tone={tone}
                onToggle={toggleSidebar}
              />
            }
          />
        </aside>
        <dialog
          ref={menuRef}
          onClick={(event) => {
            if (event.target === event.currentTarget) closeMenu();
          }}
          className={clsx(
            "m-0 flex h-dvh max-h-dvh w-64 flex-col overflow-hidden p-0",
            tone === "admin"
              ? "bg-admin text-on-brand"
              : "border-r border-default bg-background text-foreground",
            "-translate-x-full open:translate-x-0 starting:open:-translate-x-full",
            "backdrop:bg-black/0 open:backdrop:bg-black/40 starting:open:backdrop:bg-black/0",
            "transition-[translate,display,overlay] transition-discrete duration-200 backdrop:transition-[background-color,display,overlay] backdrop:transition-discrete backdrop:duration-200",
            "motion-reduce:transition-none motion-reduce:backdrop:transition-none",
          )}
        >
          <Sidebar
            label={label}
            tone={tone}
            user={user}
            items={items}
            onNavigate={closeMenu}
            onSignOut={openSignOut}
            headerAction={
              <button
                type="button"
                title="Close menu"
                aria-label="Close menu"
                onClick={closeMenu}
                className={clsx(
                  "flex size-8 shrink-0 items-center justify-center rounded-lg",
                  "focus-visible:outline-2 focus-visible:outline-offset-2",
                  tone === "admin"
                    ? "text-on-brand/85 hover:bg-admin-active/60 focus-visible:outline-on-brand"
                    : "text-fg-secondary hover:bg-subtle focus-visible:outline-brand-border",
                )}
              >
                <X aria-hidden className="size-4" />
              </button>
            }
          />
        </dialog>
        <div className="flex min-w-0 flex-1 flex-col">
          <Navbar
            title={title}
            onOpenMenu={() => menuRef.current?.showModal()}
          />
          <main className="flex-1 bg-subtle p-4 md:p-8">{children}</main>
        </div>
      </div>
      <ConfirmDialog
        open={signOutOpen}
        title="Log out?"
        message="You'll be signed out on this device and have to sign in again."
        confirmLabel="Log out"
        confirmVariant="danger"
        pending={signingOut}
        onConfirm={() => startSignOut(() => handleSignOut())}
        onCancel={closeSignOut}
      />
    </Provider>
  );
}
