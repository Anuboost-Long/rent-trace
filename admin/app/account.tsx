"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { handleSignOut } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import Button from "@/components/common/button";
import type { Me } from "@/types/auth/models";
import { useAtomValue } from "jotai";
import { useHydrateAtoms } from "jotai/utils";

export default function Account({ user }: Readonly<{ user: Me }>) {
  useHydrateAtoms([[UserAtom, user]]);
  const current = useAtomValue(UserAtom) ?? user;

  return (
    <AuthCard
      heading={`Hi ${current.first_name}`}
      message={`Signed in as ${current.email}${current.roles.length ? ` · ${current.roles.join(", ").toLowerCase()}` : ""}`}
    >
      <form action={handleSignOut}>
        <Button type="submit" variant="quiet">
          Sign out
        </Button>
      </form>
    </AuthCard>
  );
}
