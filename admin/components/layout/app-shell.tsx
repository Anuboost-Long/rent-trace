"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
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
import { useCallback, useEffect, useRef, useState } from "react";

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
          <div className="min-h-0 flex-1 overflow-y-auto">
            <Sidebar
              label={label}
              tone={tone}
              user={user}
              items={items}
              footerSlot={
                <SidebarToggle
                  collapsed={collapsed}
                  tone={tone}
                  onToggle={toggleSidebar}
                />
              }
            />
          </div>
        </aside>
        <dialog
          ref={menuRef}
          onClick={(event) => {
            if (event.target === event.currentTarget) closeMenu();
          }}
          className={clsx(
            "m-0 h-full max-h-none w-64 p-0",
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
            footerSlot={
              <Button
                variant="secondary"
                onClick={closeMenu}
                size="sm"
                className="gap-2"
              >
                <X aria-hidden className="size-4" />
                Close menu
              </Button>
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
    </Provider>
  );
}
