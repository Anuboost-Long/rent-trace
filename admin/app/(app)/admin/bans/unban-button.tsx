"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import { handleLiftBan } from "@/api/services/bans/serve-action";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import type { ApiFailure } from "@/types/api/common";
import type { Ban } from "@/types/security/models";
import { useAtomValue } from "jotai";
import { ShieldOff } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "@/utils/toast";

export default function UnbanButton({ ban }: Readonly<{ ban: Ban }>) {
  const router = useRouter();
  const me = useAtomValue(UserAtom);
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  if (ban.status !== "ACTIVE" || !me?.permissions.includes("bans.manage")) {
    return null;
  }
  const target = ban.value ?? `${ban.user?.first_name} ${ban.user?.last_name}`;

  const close = () => {
    setOpen(false);
    setReason("");
    setError(null);
  };

  const confirm = async () => {
    setPending(true);
    const { error } = await handleLiftBan(ban.id, reason.trim());
    setPending(false);
    setError(error);
    if (error) {
      toast.error(error.message);
      return;
    }
    toast.success("Ban lifted");
    close();
    router.refresh();
  };

  return (
    <>
      <Button
        variant="quiet"
        size="icon"
        title="Unban"
        aria-label={`Unban ${target}`}
        onClick={() => setOpen(true)}
      >
        <ShieldOff aria-hidden className="size-4" />
      </Button>
      {open && (
        <ConfirmDialog
          open
          title={`Unban ${target}?`}
          message="They will be able to sign in or sign up again. The ban stays in the list as lifted."
          confirmLabel="Unban"
          pending={pending}
          confirmDisabled={reason.trim() === ""}
          error={error?.fields.reason ?? error?.message}
          onConfirm={confirm}
          onCancel={close}
        >
          <TextInput
            label="Reason"
            name="reason"
            placeholder="Why the ban is being lifted"
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            required
          />
        </ConfirmDialog>
      )}
    </>
  );
}
