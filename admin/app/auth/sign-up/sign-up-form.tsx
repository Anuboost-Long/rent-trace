"use client";
import Button from "@/components/common/button";
import RadioInput from "@/components/common/inputs/radio-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useAuth from "@/hooks/form/useAuth";
import type { Role } from "@/types/auth/models";
import Link from "next/link";

type SignUpFormProp = Readonly<{ onSent: (email: string) => void }>;

export default function SignUpForm({ onSent }: SignUpFormProp) {
  const { pending, error, signUp } = useAuth();

  return (
    <form
      onSubmit={async (event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const body = {
          first_name: String(form.get("first_name")),
          last_name: String(form.get("last_name")),
          email: String(form.get("email")),
          password: String(form.get("password")),
          role: String(form.get("role")) as Role,
        };
        if (await signUp(body)) onSent(body.email);
      }}
      className="flex flex-col gap-4"
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <TextInput
          label="First name"
          name="first_name"
          autoComplete="given-name"
          required
          error={error?.fields.first_name}
        />
        <TextInput
          label="Last name"
          name="last_name"
          autoComplete="family-name"
          required
          error={error?.fields.last_name}
        />
      </div>
      <TextInput
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        required
        error={error?.fields.email}
      />
      <TextInput
        label="Password"
        name="password"
        type="password"
        autoComplete="new-password"
        required
        error={error?.fields.password}
      />
      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1.5 text-sm font-medium">I am a</legend>
        <RadioInput name="role" value="TENANT" label="Tenant" defaultChecked />
        <RadioInput name="role" value="LANDLORD" label="Landlord" />
        {error?.fields.role && (
          <p className="text-sm text-red-600">{error.fields.role}</p>
        )}
      </fieldset>
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-red-600">
          {error.message}
        </p>
      )}
      <Button type="submit" pending={pending}>
        {pending ? "Creating account…" : "Create account"}
      </Button>
      <p className="text-sm text-foreground/70">
        Already have an account?{" "}
        <Link href={Route.auth.sign_in} className="font-medium underline">
          Sign in
        </Link>
      </p>
    </form>
  );
}
