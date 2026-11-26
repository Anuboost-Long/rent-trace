"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import type { ButtonVariant } from "@/components/common/button-class-name";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { Route } from "@/constants/web-routes";
import useUserActions, { type UserAction } from "@/hooks/form/useUserActions";
import type { UserSummary } from "@/types/users/models";
import {
  canBanUser,
  canDeleteUser,
  canEditUser,
  canToggleUser,
} from "@/utils/user-permissions";
import { useAtomValue } from "jotai";
import { useRouter } from "next/navigation";

type UserActionsProp = Readonly<{
  user: UserSummary;
  footer?: React.ReactNode;
}>;

type ActionCopy = {
  button: string;
  title: (name: string) => string;
  message: string;
  confirm: string;
  variant: ButtonVariant;
  // Asks for a reason before the action runs.
  needsReason: boolean;
};

const COPY: Record<UserAction, ActionCopy> = {
  deactivate: {
    button: "Suspend account",
    title: (name) => `Suspend ${name}?`,
    message:
      "They're logged out of every device straight away and can't log in until you reactivate the account. Their records stay as they are.",
    confirm: "Suspend account",
    variant: "secondary",
    needsReason: true,
  },
  activate: {
    button: "Reactivate account",
    title: (name) => `Reactivate ${name}?`,
    message: "They'll be able to log in again.",
    confirm: "Reactivate account",
    variant: "secondary",
    needsReason: true,
  },
  ban: {
    button: "Ban account",
    title: (name) => `Ban ${name}?`,
    message:
      "This logs them out everywhere and stops the account from logging in until the ban is lifted. Their records stay, so tenancy history isn't lost.",
    confirm: "Ban account",
    variant: "danger",
    needsReason: true,
  },
  delete: {
    button: "Delete account",
    title: (name) => `Delete ${name}?`,
    message:
      "The account is removed from RentTrace and they're logged out everywhere. This can't be undone here.",
    confirm: "Delete account",
    variant: "danger",
    needsReason: false,
  },
};

// The "Account actions" buttons on an account's page, each opening a confirm dialog.
export default function UserActions({ user, footer }: UserActionsProp) {
  const router = useRouter();
  const me = useAtomValue(UserAtom);
  const { action, setAction, pending, error, confirm, cancel } = useUserActions(
    user.id,
    () => router.replace(Route.admin.users),
  );

  if (!me) return null;
  const name = `${user.first_name} ${user.last_name}`;
  const isActive = user.account_status === "ACTIVE";
  const actions: UserAction[] = [
    ...(canToggleUser(me, user) ? [isActive ? "deactivate" : "activate"] : []),
    ...(canBanUser(me, user) ? ["ban"] : []),
    ...(canDeleteUser(me, user) ? ["delete"] : []),
  ] as UserAction[];

  return (
    <>
      <div className="flex flex-col gap-3">
        {actions.map((kind) => (
          <Button
            key={kind}
            variant={COPY[kind].variant}
            onClick={() => setAction(kind)}
            className="w-full"
          >
            {COPY[kind].button}
          </Button>
        ))}
        {canEditUser(me) && (
          <ButtonLink
            href={Route.admin.user_edit(user.id)}
            variant="secondary"
            className="w-full"
          >
            Edit details
          </ButtonLink>
        )}
        {footer}
      </div>
      {action && (
        <ConfirmDialog
          open
          title={COPY[action].title(name)}
          message={COPY[action].message}
          confirmLabel={COPY[action].confirm}
          confirmVariant={COPY[action].variant}
          reasonLabel={
            COPY[action].needsReason ? "Reason (required)" : undefined
          }
          pending={pending}
          error={error?.fields.reason ?? error?.message}
          onConfirm={confirm}
          onCancel={cancel}
        />
      )}
    </>
  );
}
