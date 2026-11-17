"use client";
import AuthCard from "@/components/common/auth-card";
import Button from "@/components/common/button";
import CheckInput from "@/components/common/inputs/check-input";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import usePasswordReset from "@/hooks/form/usePasswordReset";
import Link from "next/link";
import { useState } from "react";

type ResetPasswordFormProp = Readonly<{ token: string; requiresCode: boolean }>;

export default function ResetPasswordForm({
  token,
  requiresCode,
}: ResetPasswordFormProp) {
  const { pending, error, reset } = usePasswordReset();
  const [done, setDone] = useState(false);
  const linkUnusable = Boolean(error?.fields.token || error?.fields.code);

  if (done) {
    return (
      <AuthCard
        heading="Password changed"
        message="Sign in with your new password."
      >
        <Link href={Route.auth.sign_in} className="font-medium underline">
          Go to sign in
        </Link>
      </AuthCard>
    );
  }

  return (
    <AuthCard heading="Choose a new password">
      <form
        onSubmit={async (event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          const code = String(form.get("code") ?? "").trim();
          const changed = await reset({
            token,
            new_password: String(form.get("new_password")),
            sign_out_other_devices: form.get("sign_out_other_devices") === "on",
            ...(requiresCode && { code }),
          });
          if (changed) setDone(true);
        }}
        className="flex flex-col gap-4"
      >
        <TextInput
          label="New password"
          name="new_password"
          type="password"
          autoComplete="new-password"
          required
          error={error?.fields.new_password}
        />
        {requiresCode && (
          <TextInput
            label="Authenticator code"
            name="code"
            inputMode="numeric"
            autoComplete="one-time-code"
            required
            error={error?.fields.code}
          />
        )}
        <CheckInput
          label="Sign me out of my other devices"
          name="sign_out_other_devices"
          defaultChecked
        />
        {error && !error.fields.new_password && !error.fields.code && (
          <p role="alert" className="text-sm text-red-600">
            {error.fields.token ?? error.message}
          </p>
        )}
        {requiresCode && (
          <p className="text-sm text-foreground/70">
            Use the code from your authenticator app, or one of your backup
            codes.
          </p>
        )}
        <Button type="submit" pending={pending}>
          {pending ? "Saving…" : "Change password"}
        </Button>
        {linkUnusable && (
          <Link
            href={Route.auth.forgot_password}
            className="text-sm font-medium underline"
          >
            Send a new reset link
          </Link>
        )}
      </form>
    </AuthCard>
  );
}
