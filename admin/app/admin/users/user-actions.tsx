"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { Route } from "@/constants/web-routes";
import useUserActions, { type UserAction } from "@/hooks/form/useUserActions";
import type { UserSummary } from "@/types/users/models";
import {
  canDeleteUser,
  canEditUser,
  canToggleUser,
} from "@/utils/user-permissions";
import clsx from "clsx";
import { useAtomValue } from "jotai";
import {
  Pencil,
  Trash2,
  UserCheck,
  UserX,
  type LucideIcon,
} from "lucide-react";
import { useRouter } from "next/navigation";

type UserActionsProp = Readonly<{
  user: UserSummary;
  variant: "icon" | "full";
}>;

const COPY: Record<
  UserAction,
  { title: string; message: string; confirm: string }
> = {
  activate: {
    title: "Activate",
    message: "They will be able to sign in again.",
    confirm: "Activate",
  },
  deactivate: {
    title: "Deactivate",
    message:
      "They will be signed out everywhere and can't sign in until you activate them again.",
    confirm: "Deactivate",
  },
  delete: {
    title: "Delete",
    message:
      "The account is removed from RentTrace and they are signed out everywhere. This can't be undone here.",
    confirm: "Delete",
  },
};

export default function UserActions({ user, variant }: UserActionsProp) {
  const router = useRouter();
  const me = useAtomValue(UserAtom);
  const { action, setAction, pending, error, confirm, cancel } = useUserActions(
    user.id,
    () => router.replace(Route.admin.users),
  );

  if (!me) return null;
  const canEdit = canEditUser(me);
  const canToggle = canToggleUser(me, user);
  const canDelete = canDeleteUser(me, user);
  if (!canEdit && !canToggle && !canDelete) return null;
  const name = `${user.first_name} ${user.last_name}`;
  const isActive = user.account_status === "ACTIVE";

  const buttons: {
    action: UserAction;
    label: string;
    Icon: LucideIcon;
    show: boolean;
  }[] = [
    {
      action: isActive ? "deactivate" : "activate",
      label: isActive ? "Deactivate" : "Activate",
      Icon: isActive ? UserX : UserCheck,
      show: canToggle,
    },
    { action: "delete", label: "Delete", Icon: Trash2, show: canDelete },
  ];

  return (
    <>
      <div className={clsx("flex gap-2", variant === "icon" && "justify-end")}>
        {canEdit && <EditButton user={user} name={name} variant={variant} />}
        {buttons
          .filter((button) => button.show)
          .map(({ action: kind, label, Icon }) => (
            <Button
              key={kind}
              variant="quiet"
              onClick={() => setAction(kind)}
              aria-label={variant === "icon" ? `${label} ${name}` : undefined}
              title={variant === "icon" ? label : undefined}
              size={variant === "icon" ? "icon" : "md"}
              className={clsx(variant === "full" && "gap-2")}
            >
              <Icon aria-hidden className="size-4" />
              {variant === "full" && label}
            </Button>
          ))}
      </div>
      {action && (
        <ConfirmDialog
          open
          title={`${COPY[action].title} ${name}?`}
          message={COPY[action].message}
          confirmLabel={COPY[action].confirm}
          pending={pending}
          error={error?.message}
          onConfirm={confirm}
          onCancel={cancel}
        />
      )}
    </>
  );
}

function EditButton({
  user,
  name,
  variant,
}: Readonly<UserActionsProp & { name: string }>) {
  if (variant === "icon") {
    return (
      <ButtonLink
        href={Route.admin.user_edit(user.id)}
        variant="quiet"
        aria-label={`Edit ${name}`}
        title="Edit"
        size="icon"
      >
        <Pencil aria-hidden className="size-4" />
      </ButtonLink>
    );
  }
  return (
    <ButtonLink
      href={Route.admin.user_edit(user.id)}
      variant="quiet"
      className="gap-2"
    >
      <Pencil aria-hidden className="size-4" />
      Edit
    </ButtonLink>
  );
}
