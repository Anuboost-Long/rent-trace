"use client";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import usePasswordReset from "@/hooks/form/usePasswordReset";
import Link from "next/link";

export default function ForgotPasswordForm() {
  const { pending, error, notice, requestLink } = usePasswordReset();

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        requestLink(String(new FormData(event.currentTarget).get("email")));
      }}
      className="flex flex-col gap-4"
    >
      <TextInput
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        required
        error={error?.fields.email}
      />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}
      <Button type="submit" pending={pending}>
        {pending ? "Sending…" : "Send reset link"}
      </Button>
      <p className="text-sm">
        <Link href={Route.auth.sign_in} className="font-medium underline">
          Back to sign in
        </Link>
      </p>
    </form>
  );
}
