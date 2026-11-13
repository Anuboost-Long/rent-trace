"use client";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextArea from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import { IssuePriorityLabel } from "@/constants/maintenance";
import useIssueActions from "@/hooks/form/useIssueActions";
import type { IssuePriority } from "@/types/maintenance/models";
import type { ServiceCategory } from "@/types/providers/models";
import { Plus } from "lucide-react";
import { useState } from "react";

export type ReportableTenancy = { id: number; label: string };

const priorityOptions = Object.entries(IssuePriorityLabel).map(
  ([value, label]) => ({ value, label }),
);

type ReportIssueButtonProp = Readonly<{
  tenancies: ReportableTenancy[];
  categories: ServiceCategory[];
}>;

export default function ReportIssueButton({
  tenancies,
  categories,
}: ReportIssueButtonProp) {
  const { pending, error, report, clearError } = useIssueActions("tenant");
  const [open, setOpen] = useState(false);
  const [tenancyId, setTenancyId] = useState(String(tenancies[0]?.id ?? ""));
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<IssuePriority>("MEDIUM");
  const [category, setCategory] = useState("");

  if (tenancies.length === 0) return null;
  const fields = error?.fields ?? {};

  const close = () => {
    setOpen(false);
    clearError();
  };

  const send = async () => {
    await report({
      tenancy_id: Number(tenancyId),
      title: title.trim(),
      description: description.trim(),
      priority,
      category_code: category || null,
    });
  };

  return (
    <>
      <Button className="gap-2" onClick={() => setOpen(true)}>
        <Plus aria-hidden className="size-4" />
        Report an issue
      </Button>
      {open && (
        <ConfirmDialog
          open
          title="Report an issue"
          message="Your landlord is told straight away. You can follow what happens next here."
          confirmLabel="Send report"
          pending={pending}
          confirmDisabled={title.trim() === "" || description.trim() === ""}
          error={
            error && Object.keys(fields).length === 0
              ? error.message
              : undefined
          }
          onConfirm={send}
          onCancel={close}
        >
          <div className="space-y-4">
            {tenancies.length > 1 && (
              <SelectInput
                label="Where"
                name="tenancy"
                value={tenancyId}
                onValueChange={setTenancyId}
                options={tenancies.map((item) => ({
                  value: String(item.id),
                  label: item.label,
                }))}
                error={fields.tenancy_id}
              />
            )}
            <TextInput
              label="What is wrong"
              name="title"
              placeholder="Kitchen tap drips"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              error={fields.title}
              required
            />
            <TextArea
              label="Details"
              name="description"
              placeholder="When it started, where it is, anything that helps"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              error={fields.description}
              required
            />
            <SelectInput
              label="Kind of problem (optional)"
              name="category"
              value={category}
              onValueChange={setCategory}
              options={[
                { value: "", label: "Not sure" },
                ...categories.map(({ code, name }) => ({
                  value: code,
                  label: name,
                })),
              ]}
              error={fields.category_code}
            />
            <SelectInput
              label="How urgent"
              name="priority"
              value={priority}
              onValueChange={(value) => setPriority(value as IssuePriority)}
              options={priorityOptions}
              error={fields.priority}
            />
          </div>
        </ConfirmDialog>
      )}
    </>
  );
}
