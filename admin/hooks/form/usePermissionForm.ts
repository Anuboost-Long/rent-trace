"use client";
import {
  handleCreatePermission,
  handleUpdatePermission,
} from "@/api/services/access/serve-action";
import { Route } from "@/constants/web-routes";
import type { PermissionItem } from "@/types/access/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

type Fields = {
  code: string;
  name: string;
  is_admin_only: boolean;
  is_active: boolean;
};

const usePermissionForm = (permission: PermissionItem | null) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

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
      toast.success("Permission saved");
      router.push(Route.admin.permission(data.code));
      router.refresh();
    }
  };

  return { pending, error, save };
};

export default usePermissionForm;
