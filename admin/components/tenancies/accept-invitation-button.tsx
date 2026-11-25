"use client";
import { handleAcceptInvitationById } from "@/api/services/tenancies/serve-action";
import Button from "@/components/common/button";
import type { ApiFailure } from "@/types/api/common";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function AcceptInvitationButton({
  invitationId,
}: Readonly<{ invitationId: number }>) {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<ApiFailure | null>(null);

  const accept = async () => {
    setPending(true);
    setError(null);
    const { error } = await handleAcceptInvitationById(invitationId);
    setPending(false);
    setError(error);
    if (!error) router.refresh();
  };

  return (
    <div className="flex flex-col items-start gap-2 sm:items-end">
      <Button onClick={accept} pending={pending}>
        {pending ? "Joining…" : "Accept invitation"}
      </Button>
      {error && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
    </div>
  );
}
