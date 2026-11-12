"use client";
import Button from "@/components/common/button";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import {
  RequestActionCopy,
  type RequestAction,
} from "@/constants/contact-requests";
import useContactRequestAction from "@/hooks/form/useContactRequestAction";

type RequestActionsProp = Readonly<{
  requestId: number;
  actions: RequestAction[];
}>;

export default function RequestActions({
  requestId,
  actions,
}: RequestActionsProp) {
  const { action, setAction, pending, error, confirm, cancel } =
    useContactRequestAction(requestId);
  const copy = action && RequestActionCopy[action];

  return (
    <div className="flex justify-end gap-2">
      {actions.map((name) => (
        <Button
          key={name}
          size="sm"
          variant={name === "accept" ? "primary" : "quiet"}
          onClick={() => setAction(name)}
        >
          {RequestActionCopy[name].button}
        </Button>
      ))}
      {copy && (
        <ConfirmDialog
          open
          title={copy.title}
          message={copy.message}
          confirmLabel={copy.button}
          pending={pending}
          error={error?.message}
          onConfirm={confirm}
          onCancel={cancel}
        />
      )}
    </div>
  );
}
