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
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const INVITATION_DONE: Record<InvitationAction, string> = {
  resend: "Invitation sent again",
  revoke: "Invitation cancelled",
  approve: "Request approved",
  decline: "Request declined",
};

const useInvitations = (audience: TenancyAudience, tenancyId: number) => {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const finish = (failure: ApiFailure | null, done: string) => {
    setPending(false);
    setError(failure);
    if (!failure) {
      toast.success(done);
      router.refresh();
    }
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
    return finish(error, "Invitation sent");
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
    return finish(error, INVITATION_DONE[action]);
  };

  return { pending, error, invite, act };
};

export default useInvitations;
