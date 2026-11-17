"use client";
import Button from "@/components/common/button";
import { Route } from "@/constants/web-routes";
import useAuth from "@/hooks/form/useAuth";
import { Mail } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

type CheckEmailProp = Readonly<{
  email: string;
  onChangeEmail: () => void;
}>;

const RESEND_COOLDOWN_SECONDS = 30;

export default function CheckEmail({ email, onChangeEmail }: CheckEmailProp) {
  const { pending, error, notice, resendVerification } = useAuth();
  const [cooldown, setCooldown] = useState(0);

  useEffect(() => {
    if (cooldown === 0) return;
    const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
    return () => clearTimeout(timer);
  }, [cooldown]);

  const resend = async () => {
    await resendVerification(email);
    setCooldown(RESEND_COOLDOWN_SECONDS);
  };

  return (
    <div className="animate-panel-in motion-reduce:animate-none">
      <span className="flex size-12 items-center justify-center rounded-lg border border-foreground/15">
        <Mail aria-hidden className="size-6" strokeWidth={1.5} />
      </span>
      <p className="mt-4 text-foreground/70">
        We sent a confirmation link to{" "}
        <span className="font-medium text-foreground">{email}</span>. Open it to
        finish creating your account.
      </p>
      <p className="mt-2 text-sm text-foreground/70">
        Nothing there? Check your spam folder, or send it again.
      </p>
      <div className="mt-6 flex flex-col gap-3">
        <Button
          variant="quiet"
          onClick={resend}
          pending={pending}
          disabled={cooldown > 0}
        >
          {cooldown > 0 ? `Send again in ${cooldown}s` : "Send again"}
        </Button>
        {notice && (
          <p role="status" className="text-sm">
            {notice}
          </p>
        )}
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error.message}
          </p>
        )}
      </div>
      <div className="mt-6 flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
        <button
          type="button"
          onClick={onChangeEmail}
          className="font-medium underline"
        >
          Use a different email
        </button>
        <Link href={Route.auth.sign_in} className="font-medium underline">
          Back to sign in
        </Link>
      </div>
    </div>
  );
}
