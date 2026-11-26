"use client";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import { Route } from "@/constants/web-routes";
import useAuth from "@/hooks/form/useAuth";
import Link from "next/link";
import { useRef } from "react";

const EMAIL_UNVERIFIED = 403;

const LINK_CLASS =
  "font-semibold text-fg-brand hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border";

export default function SignInForm({
  redirectTo,
  sessionEnded,
}: Readonly<{ redirectTo?: string; sessionEnded?: boolean }>) {
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
      {sessionEnded && !error && (
        <div
          role="status"
          className="rounded-lg border border-warning-border bg-warning-background p-3 text-body-sm text-warning"
        >
          <p className="font-semibold">Your session ended</p>
          <p className="mt-1">
            For security, sessions end after a period of inactivity or when your
            permissions change. Log in again to continue.
          </p>
        </div>
      )}
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
        {pending ? "Logging in…" : "Log in"}
      </Button>
      {error?.status === EMAIL_UNVERIFIED && (
        <Button
          type="button"
          variant="secondary"
          pending={pending}
          onClick={() => resendVerification(readForm().email)}
        >
          Send a new verification link
        </Button>
      )}
      <p className="text-body-sm">
        <Link href={Route.auth.forgot_password} className={LINK_CLASS}>
          Forgot password?
        </Link>
      </p>
      <p className="text-body-sm text-fg-secondary">
        New to RentTrace?{" "}
        <Link href={Route.auth.sign_up} className={LINK_CLASS}>
          Create an account
        </Link>
      </p>
    </form>
  );
}
