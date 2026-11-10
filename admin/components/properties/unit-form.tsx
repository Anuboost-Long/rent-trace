import Button from "@/components/common/button";
import CheckInput from "@/components/common/inputs/check-input";
import SelectInput from "@/components/common/inputs/select-input";
import TextAreaInput from "@/components/common/inputs/text-area-input";
import TextInput from "@/components/common/inputs/text-input";
import { labelOptions, UnitTypeLabel } from "@/constants/properties";
import type { ApiFailure } from "@/types/api/common";
import type { PropertyUnit, UnitBody } from "@/types/properties/models";

type UnitFormProp = Readonly<{
  unit: PropertyUnit | null;
  pending: boolean;
  error: ApiFailure | null;
  onSubmit: (body: UnitBody) => void;
  onCancel: () => void;
}>;

export default function UnitForm({
  unit,
  pending,
  error,
  onSubmit,
  onCancel,
}: UnitFormProp) {
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        onSubmit({
          name: String(form.get("name")),
          unit_number: String(form.get("unit_number") ?? ""),
          unit_type: String(form.get("unit_type")),
          description: String(form.get("description") ?? ""),
          is_public: form.get("is_public") === "on",
        });
      }}
      className="mt-4 flex flex-col gap-4 rounded-xl border border-foreground/15 p-4"
    >
      <h3 className="text-sm font-semibold">
        {unit ? `Edit ${unit.name}` : "New unit"}
      </h3>
      <div className="grid gap-4 sm:grid-cols-2">
        <TextInput
          label="Name"
          name="name"
          defaultValue={unit?.name}
          required
          error={error?.fields.name}
        />
        <TextInput
          label="Unit number (optional)"
          name="unit_number"
          defaultValue={unit?.unit_number ?? ""}
          error={error?.fields.unit_number}
        />
      </div>
      <SelectInput
        label="Type"
        name="unit_type"
        options={labelOptions(UnitTypeLabel)}
        defaultValue={unit?.unit_type}
        error={error?.fields.unit_type}
      />
      <TextAreaInput
        label="Description (optional)"
        name="description"
        defaultValue={unit?.description ?? ""}
        error={error?.fields.description}
      />
      <CheckInput
        name="is_public"
        label="Show this unit publicly"
        defaultChecked={unit?.is_public}
      />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-red-600">
          {error.message}
        </p>
      )}
      <div className="flex gap-3">
        <Button type="submit" size="sm" pending={pending}>
          {unit ? "Save unit" : "Add unit"}
        </Button>
        <Button variant="quiet" size="sm" onClick={onCancel} disabled={pending}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
