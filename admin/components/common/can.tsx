"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { useAtomValue } from "jotai";

type CanProp = Readonly<{ permission: string; children: React.ReactNode }>;

export default function Can({ permission, children }: CanProp) {
  const me = useAtomValue(UserAtom);
  return me?.permissions.includes(permission) ? children : null;
}
