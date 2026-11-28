"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { handleRevokeToken } from "@/api/services/tokens/serve-action";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import type { ApiFailure } from "@/types/api/common";
import type { AccessToken } from "@/types/security/models";
import { useAtomValue } from "jotai";
import { LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "@/utils/toast";

export default function RevokeTokenButton({
  token,
}: Readonly<{ token: AccessToken }>) {
  const router = useRouter();
  const me = useAtomValue(UserAtom);
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  if (
    token.status !== "ACTIVE" ||
    token.is_current ||
    !me?.permissions.includes("tokens.revoke")
  ) {
    return null;
  }
  const person = `${token.user.first_name} ${token.user.last_name}`;

  const close = () => {
    setOpen(false);
    setError(null);
  };

  const confirm = async () => {
    setPending(true);
    const { error } = await handleRevokeToken(token.id);
    setPending(false);
    setError(error);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Token revoked");
    close();
    router.refresh();
  };

  return (
    <>
      <Button
        variant="quiet"
        size="icon"
        title="Revoke"
        aria-label={`Revoke ${person}'s session on ${token.device_name ?? "an unknown device"}`}
        onClick={() => setOpen(true)}
      >
        <LogOut aria-hidden className="size-4" />
      </Button>
      {open && (
        <ConfirmDialog
          open
          title={`Revoke ${person}'s session?`}
          message="They are signed out on this device straight away and have to sign in again."
          confirmLabel="Revoke"
          pending={pending}
          error={error?.message}
          onConfirm={confirm}
          onCancel={close}
        />
      )}
    </>
  );
}
