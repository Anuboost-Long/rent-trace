"use client";
import Button from "@/components/common/button";
import RadioInput from "@/components/common/inputs/radio-input";
import TextInput from "@/components/common/inputs/text-input";
import useOnboarding from "@/hooks/form/useOnboarding";
import type { Role } from "@/types/auth/models";

type OnboardingFormProp = Readonly<{ firstName: string; lastName: string }>;

export default function OnboardingForm({
  firstName,
  lastName,
}: OnboardingFormProp) {
  const { pending, error, complete } = useOnboarding();

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        complete({
          first_name: String(form.get("first_name")),
          last_name: String(form.get("last_name")),
          role: String(form.get("role")) as Role,
        });
      }}
      className="flex flex-col gap-4"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <TextInput
          label="First name"
          name="first_name"
          autoComplete="given-name"
          defaultValue={firstName}
          required
          error={error?.fields.first_name}
        />
        <TextInput
          label="Last name"
          name="last_name"
          autoComplete="family-name"
          defaultValue={lastName}
          required
          error={error?.fields.last_name}
        />
      </div>
      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1.5 text-sm font-medium">I am a</legend>
        <RadioInput name="role" value="TENANT" label="Tenant" required />
        <RadioInput name="role" value="LANDLORD" label="Landlord" />
        {error?.fields.role && (
          <p className="text-sm text-error">{error.fields.role}</p>
        )}
      </fieldset>
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      <Button type="submit" pending={pending}>
        {pending ? "Saving…" : "Continue"}
      </Button>
    </form>
  );
}
