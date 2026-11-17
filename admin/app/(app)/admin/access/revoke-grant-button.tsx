"use client";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useGrants from "@/hooks/form/useGrants";
import { Trash2 } from "lucide-react";
import { useState } from "react";

type RevokeGrantButtonProp = Readonly<{
  userId: number;
  personName: string;
  permissionCode: string;
  permissionName: string;
}>;

export default function RevokeGrantButton({
  userId,
  personName,
  permissionCode,
  permissionName,
}: RevokeGrantButtonProp) {
  const { pending, error, revoke } = useGrants(userId);
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        variant="quiet"
        size="icon"
        title="Revoke"
        aria-label={`Revoke ${permissionName} from ${personName}`}
        onClick={() => setOpen(true)}
      >
        <Trash2 aria-hidden className="size-4" />
      </Button>
      {open && (
        <ConfirmDialog
          open
          title={`Revoke ${permissionName}?`}
          message={`${personName} loses it unless a role gives it to them.`}
          confirmLabel="Revoke"
          pending={pending}
          error={error?.message}
          onConfirm={async () => {
            if (await revoke(permissionCode)) setOpen(false);
          }}
          onCancel={() => setOpen(false)}
        />
      )}
    </>
  );
}
