"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import type { Me } from "@/types/auth/models";
import { createStore, Provider } from "jotai";
import { useEffect, useState } from "react";

type UserProviderProp = Readonly<{ user: Me; children: React.ReactNode }>;

export default function UserProvider({ user, children }: UserProviderProp) {
  const [store] = useState(() => {
    const created = createStore();
    created.set(UserAtom, user);
    return created;
  });
  useEffect(() => {
    store.set(UserAtom, user);
  }, [store, user]);

  return <Provider store={store}>{children}</Provider>;
}
