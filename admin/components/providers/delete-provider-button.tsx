"use client";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useDeleteProvider from "@/hooks/form/useDeleteProvider";
import { Trash2 } from "lucide-react";

type DeleteProviderButtonProp = Readonly<{ id: number; name: string }>;

export default function DeleteProviderButton({
  id,
  name,
}: DeleteProviderButtonProp) {
  const { confirming, setConfirming, pending, error, confirm, cancel } =
    useDeleteProvider(id);

  return (
    <>
      <Button
        variant="quiet"
        className="gap-2"
        onClick={() => setConfirming(true)}
      >
        <Trash2 aria-hidden className="size-4" />
        Delete
      </Button>
      <ConfirmDialog
        open={confirming}
        title={`Delete ${name}?`}
        message="They are removed from your list and from every property they are linked to. Tenants will no longer see their details."
        confirmLabel="Delete"
        pending={pending}
        error={error?.message}
        onConfirm={confirm}
        onCancel={cancel}
      />
    </>
  );
}
