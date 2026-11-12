"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { TenancyAccess } from "@/constants/tenancies";
import useTenancyActions from "@/hooks/form/useTenancyActions";
import type {
  TenancyAction,
  TenancyAudience,
  TenancyStatus,
} from "@/types/tenancies/models";

type TenancyActionsProp = Readonly<{
  audience: TenancyAudience;
  tenancyId: number;
  status: TenancyStatus;
}>;

const COPY: Record<
  TenancyAction,
  {
    button: string;
    title: string;
    message: string;
    cancelLabel: string;
  }
> = {
  activate: {
    button: "Start tenancy",
    title: "Start this tenancy?",
    message:
      "It becomes active and the tenants are told it has started. You need at least one tenant, and the unit can't have another active tenancy in the same period.",
    cancelLabel: "Not yet",
  },
  end: {
    button: "End tenancy",
    title: "End this tenancy?",
    message:
      "Today becomes the end date unless it already ended earlier, and every tenant is marked as having left. This can't be undone.",
    cancelLabel: "Keep tenancy",
  },
  cancel: {
    button: "Cancel tenancy",
    title: "Cancel this tenancy?",
    message:
      "It never starts and any tenants who joined are released. This can't be undone.",
    cancelLabel: "Keep tenancy",
  },
};

const ACTIONS_FOR: Partial<Record<TenancyStatus, TenancyAction[]>> = {
  DRAFT: ["activate", "cancel"],
  PENDING: ["cancel"],
  ACTIVE: ["end"],
};

export default function TenancyActions({
  audience,
  tenancyId,
  status,
}: TenancyActionsProp) {
  const { action, setAction, pending, error, confirm, cancel } =
    useTenancyActions(audience, tenancyId);
  const available = ACTIONS_FOR[status] ?? [];
  if (available.length === 0) return null;

  return (
    <Can permission={TenancyAccess[audience].update}>
      <div className="flex gap-2">
        {available.map((kind) => (
          <Button
            key={kind}
            variant={kind === "activate" ? undefined : "quiet"}
            onClick={() => setAction(kind)}
          >
            {COPY[kind].button}
          </Button>
        ))}
      </div>
      {action && (
        <ConfirmDialog
          open
          title={COPY[action].title}
          message={COPY[action].message}
          confirmLabel={COPY[action].button}
          cancelLabel={COPY[action].cancelLabel}
          pending={pending}
          error={error?.fields.status ?? error?.message}
          onConfirm={confirm}
          onCancel={cancel}
        />
      )}
    </Can>
  );
}
