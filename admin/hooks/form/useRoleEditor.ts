"use client";
import {
  handleCreateRole,
  handleUpdateRole,
} from "@/api/services/access/serve-action";
import { Route } from "@/constants/web-routes";
import type { RoleItem } from "@/types/access/models";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useRoleEditor = (role: RoleItem | null, allRoles: RoleItem[]) => {
  const router = useRouter();
  const [direct, setDirect] = useState(() => new Set(role?.permissions ?? []));
  const [parent, setParent] = useState(role?.parent ?? "");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const parentRole = allRoles.find((candidate) => candidate.code === parent);
  const inherited = new Set(
    parentRole
      ? [...parentRole.permissions, ...parentRole.inherited_permissions]
      : [],
  );

  const toggle = (code: string) =>
    setDirect((current) => {
      const next = new Set(current);
      if (!next.delete(code)) next.add(code);
      return next;
    });

  const save = async (fields: {
    name: string;
    description: string;
    is_active?: boolean;
  }) => {
    setPending(true);
    setError(null);
    const body = {
      ...fields,
      parent: parent || null,
      permissions: [...direct].filter((code) => !inherited.has(code)),
    };
    const { error } = role
      ? await handleUpdateRole(role.code, body)
      : await handleCreateRole(body);
    setPending(false);
    setError(error);
    if (error) return;
    router.push(Route.admin.roles);
    router.refresh();
  };

  return { direct, inherited, parent, setParent, toggle, save, pending, error };
};

export default useRoleEditor;
