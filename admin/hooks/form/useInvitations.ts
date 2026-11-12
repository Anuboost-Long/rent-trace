"use client";
import {
  handleInvitationAction,
  handleInviteTenant,
} from "@/api/services/tenancies/serve-action";
import type { ApiFailure } from "@/types/api/common";
import type {
  InvitationAction,
  TenancyAudience,
} from "@/types/tenancies/models";
import { useRouter } from "next/navigation";
import { useState } from "react";

const useInvitations = (audience: TenancyAudience, tenancyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const finish = (failure: ApiFailure | null) => {
    setPending(false);
    setError(failure);
    if (!failure) router.refresh();
    return !failure;
  };

  const invite = async (email: string, isPrimary: boolean) => {
    setPending(true);
    setError(null);
    const { error } = await handleInviteTenant(
      tenancyId,
      { email, is_primary: isPrimary },
      audience,
    );
    return finish(error);
  };

  const act = async (invitationId: number, action: InvitationAction) => {
    setPending(true);
    setError(null);
    const { error } = await handleInvitationAction(
      tenancyId,
      invitationId,
      action,
      audience,
    );
    return finish(error);
  };

  return { pending, error, invite, act };
};

export default useInvitations;
