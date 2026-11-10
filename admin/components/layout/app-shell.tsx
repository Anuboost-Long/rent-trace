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
import { useCallback, useEffect, useRef, useState } from "react";

import Navbar from "./navbar";
import Sidebar from "./sidebar";
import SidebarToggle from "./sidebar-toggle";

type AppShellProp = Readonly<{
  audience: Audience;
  user: Me;
  sidebarCollapsed: boolean;
  children: React.ReactNode;
}>;

const ONE_YEAR_SECONDS = 365 * 24 * 60 * 60;

export default function AppShell({
  audience,
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
  const { label } = Navigation[audience];
  const items = Navigation[audience].items.filter(
    (item) => !item.permission || user.permissions.includes(item.permission),
  );
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
            "border-r border-foreground/15",
            "transition-[width] duration-150 motion-reduce:transition-none",
          )}
        >
          <div className="min-h-0 flex-1 overflow-y-auto">
            <Sidebar label={label} items={items} />
          </div>
          <SidebarToggle collapsed={collapsed} onToggle={toggleSidebar} />
        </aside>
        <dialog
          ref={menuRef}
          onClick={(event) => {
            if (event.target === event.currentTarget) closeMenu();
          }}
          className={clsx(
            "m-0 h-full max-h-none w-64 p-0",
            "border-r border-foreground/15 bg-background text-foreground",
            "-translate-x-full open:translate-x-0 starting:open:-translate-x-full",
            "backdrop:bg-black/0 open:backdrop:bg-black/40 starting:open:backdrop:bg-black/0",
            "transition-[translate,display,overlay] transition-discrete duration-200 backdrop:transition-[background-color,display,overlay] backdrop:transition-discrete backdrop:duration-200",
            "motion-reduce:transition-none motion-reduce:backdrop:transition-none",
          )}
        >
          <Sidebar label={label} items={items} onNavigate={closeMenu} />
          <Button
            variant="quiet"
            onClick={closeMenu}
            size="sm"
            className="mx-4 gap-2"
          >
            <X aria-hidden className="size-4" />
            Close
          </Button>
        </dialog>
        <div className="flex min-w-0 flex-1 flex-col">
          <Navbar onOpenMenu={() => menuRef.current?.showModal()} />
          <main className="flex-1 p-4 md:p-8">{children}</main>
        </div>
      </div>
    </Provider>
  );
}
