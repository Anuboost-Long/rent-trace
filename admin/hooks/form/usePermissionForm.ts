"use client";
import {
  handleCreatePermission,
  handleUpdatePermission,
} from "@/api/services/access/serve-action";
import { Route } from "@/constants/web-routes";
import type { PermissionItem } from "@/types/access/models";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

type Fields = {
  code: string;
  name: string;
  is_admin_only: boolean;
  is_active: boolean;
};

const usePermissionForm = (permission: PermissionItem | null) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const save = async (fields: Fields) => {
    setPending(true);
    setError(null);
    const { data, error } = permission
      ? await handleUpdatePermission(permission.code, {
          name: fields.name,
          is_admin_only: fields.is_admin_only,
          is_active: fields.is_active,
        })
      : await handleCreatePermission({
          code: fields.code,
          name: fields.name,
          is_admin_only: fields.is_admin_only,
        });
    setPending(false);
    setError(error);
    if (data) {
      router.push(Route.admin.permission(data.code));
      router.refresh();
    }
  };

  return { pending, error, save };
};

export default usePermissionForm;
