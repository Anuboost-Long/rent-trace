"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import TextArea from "@/components/common/inputs/text-area-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useResetAuthenticator from "@/hooks/form/useResetAuthenticator";
import clsx from "clsx";
import { useAtomValue } from "jotai";
import { Mail, ShieldOff } from "lucide-react";
import { useState } from "react";

type ResetAuthenticatorButtonProp = Readonly<{
  userId: number;
  name: string;
  hasAuthenticator: boolean;
  authenticatorWasReset: boolean;
}>;

export default function ResetAuthenticatorButton({
  userId,
  name,
  hasAuthenticator,
  authenticatorWasReset,
}: ResetAuthenticatorButtonProp) {
  const me = useAtomValue(UserAtom);
  const {
    open,
    setOpen,
    pending,
    error,
    close,
    reset,
    emailSent,
    resending,
    resend,
  } = useResetAuthenticator(userId);
  const [reason, setReason] = useState("");

  if (!me?.is_top_level_admin || me.id === userId) return null;

  const closeAndClear = () => {
    setReason("");
    close();
  };

  return (
    <>
      {hasAuthenticator && (
        <Button
          variant="secondary"
          className="w-full gap-2"
          onClick={() => setOpen(true)}
        >
          <ShieldOff aria-hidden className="size-4" />
          Reset authenticator
        </Button>
      )}
      {authenticatorWasReset && (
        <Button
          variant="secondary"
          className="w-full gap-2"
          pending={resending}
          onClick={resend}
        >
          <Mail aria-hidden className="size-4" />
          Resend reset email
        </Button>
      )}
      {emailSent !== null && (
        <p
          role="status"
          className={clsx(
            "text-body-sm",
            emailSent ? "text-fg-secondary" : "text-red-600",
          )}
        >
          {emailSent
            ? "Reset email sent."
            : "The reset email couldn't be sent. Check the mail connection, then use Resend reset email."}
        </p>
      )}
      {open && (
        <ConfirmDialog
          open
          title={`Reset ${name}'s authenticator?`}
          message="They are signed out everywhere and emailed. Next time they sign in they set up a new authenticator. Confirm who is asking outside the app first."
          confirmLabel="Reset authenticator"
          confirmDisabled={reason.trim() === ""}
          pending={pending}
          error={error?.fields.reason ? undefined : error?.message}
          onConfirm={() => reset(reason.trim())}
          onCancel={closeAndClear}
        >
          <TextArea
            label="Reason"
            name="reason"
            rows={3}
            value={reason}
            onChange={(event) => setReason(event.target.value)}
            error={error?.fields.reason}
          />
        </ConfirmDialog>
      )}
    </>
  );
}
