"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import ComboboxInput from "@/components/common/inputs/combobox-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { BanDurationLabel, CreatableBanTypeLabel } from "@/constants/security";
import useCreateBan, { findPeople } from "@/hooks/form/useCreateBan";
import type { CreatableBanType } from "@/types/security/models";
import { Ban } from "lucide-react";

const toOptions = (labels: Record<string, string>) =>
  Object.entries(labels).map(([value, label]) => ({ value, label }));

export default function CreateBanButton() {
  const ban = useCreateBan();
  const fields = ban.error?.fields ?? {};

  return (
    <Can permission="bans.manage">
      <Button className="gap-2" onClick={() => ban.setOpen(true)}>
        <Ban aria-hidden className="size-4" />
        Ban
      </Button>
      {ban.open && (
        <ConfirmDialog
          open
          title="Ban"
          message="Banned people are signed out and can't sign in or sign up. You can lift a ban later."
          confirmLabel="Ban"
          pending={ban.pending}
          confirmDisabled={!ban.canSubmit}
          error={ban.error?.message}
          onConfirm={ban.submit}
          onCancel={ban.close}
        >
          <div className="space-y-4">
            <SelectInput
              label="Ban"
              name="ban_type"
              value={ban.type}
              onValueChange={(next) => ban.setType(next as CreatableBanType)}
              options={toOptions(CreatableBanTypeLabel)}
            />
            {ban.type === "ACCOUNT" ? (
              <ComboboxInput
                label="Person"
                name="user_id"
                value={ban.person?.label ?? ""}
                loadOptions={findPeople}
                placeholder="Search by name or email"
                emptyMessage="No one matches"
                error={fields.user_id}
                onSelect={ban.setPerson}
              />
            ) : (
              <TextInput
                label={ban.type === "EMAIL" ? "Email" : "Domain"}
                name="value"
                placeholder={
                  ban.type === "EMAIL" ? "name@example.com" : "example.com"
                }
                value={ban.value}
                error={fields.value}
                onChange={(event) => ban.setValue(event.target.value)}
                required
              />
            )}
            <TextInput
              label="Reason"
              name="reason"
              placeholder="Why this is being banned"
              value={ban.reason}
              error={fields.reason}
              onChange={(event) => ban.setReason(event.target.value)}
              required
            />
            <SelectInput
              label="Duration"
              name="duration"
              value={ban.duration}
              onValueChange={ban.setDuration}
              error={fields.expires_at}
              options={toOptions(BanDurationLabel)}
            />
          </div>
        </ConfirmDialog>
      )}
    </Can>
  );
}
