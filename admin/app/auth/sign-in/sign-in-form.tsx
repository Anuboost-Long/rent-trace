"use client";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useAuth from "@/hooks/form/useAuth";
import Link from "next/link";
import { useRef } from "react";

const EMAIL_UNVERIFIED = 403;

export default function SignInForm({
  redirectTo,
}: Readonly<{ redirectTo?: string }>) {
  const formRef = useRef<HTMLFormElement>(null);
  const { pending, error, notice, signIn, resendVerification } = useAuth();

  const readForm = () => {
    const form = new FormData(formRef.current!);
    return {
      email: String(form.get("email")),
      password: String(form.get("password")),
    };
  };

  return (
    <form
      ref={formRef}
      onSubmit={(event) => {
        event.preventDefault();
        signIn(readForm(), redirectTo);
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
      <TextInput
        label="Password"
        name="password"
        type="password"
        autoComplete="current-password"
        required
        error={error?.fields.password}
      />
      {error && Object.keys(error.fields).length === 0 && (
        <p role="alert" className="text-sm text-error">
          {error.message}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}
      <Button type="submit" pending={pending}>
        {pending ? "Signing in…" : "Sign in"}
      </Button>
      {error?.status === EMAIL_UNVERIFIED && (
        <Button
          type="button"
          variant="quiet"
          pending={pending}
          onClick={() => resendVerification(readForm().email)}
        >
          Send a new verification link
        </Button>
      )}
      <p className="text-sm">
        <Link
          href={Route.auth.forgot_password}
          className="font-medium underline"
        >
          Forgot password?
        </Link>
      </p>
      <p className="text-sm text-fg-secondary">
        New to RentTrace?{" "}
        <Link href={Route.auth.sign_up} className="font-medium underline">
          Create an account
        </Link>
      </p>
    </form>
  );
}
