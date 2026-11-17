"use client";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useDeleteProperty from "@/hooks/form/useDeleteProperty";
import { Trash2 } from "lucide-react";

type DeletePropertyButtonProp = Readonly<{ id: number; title: string }>;

export default function DeletePropertyButton({
  id,
  title,
}: DeletePropertyButtonProp) {
  const { confirming, setConfirming, pending, error, confirm, cancel } =
    useDeleteProperty(id);

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
        title={`Delete ${title}?`}
        message="The property and its units are removed from RentTrace. A property with tenancies can't be deleted."
        confirmLabel="Delete"
        pending={pending}
        error={error?.message}
        onConfirm={confirm}
        onCancel={cancel}
      />
    </>
  );
}
