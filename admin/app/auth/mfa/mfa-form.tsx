"use client";
import { handleSignOut } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import Button from "@/components/common/button";
import OtpInput from "@/components/common/inputs/otp-input";
import TextInput from "@/components/common/inputs/text-input";
import useMfa from "@/hooks/form/useMfa";
import type { MfaStatus } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import QRCode from "react-qr-code";

type MfaFormProp = Readonly<{ status: MfaStatus; destination: string }>;

const ADMIN_TAG = "Admin";
const LINK_BUTTON_CLASS =
  "text-body-sm font-semibold text-fg-brand hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border";

// "JBSWY3DPEHPK3PXP" reads more easily as "JBSW Y3DP EHPK 3PXP".
const groupInFours = (secret: string) =>
  secret.match(/.{1,4}/g)?.join(" ") ?? secret;

const readCode = (event: React.FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  return String(new FormData(event.currentTarget).get("code")).trim();
};

function BackToLogIn() {
  return (
    <form action={handleSignOut} className="mt-4">
      <button type="submit" className={LINK_BUTTON_CLASS}>
        Back to log in
      </button>
    </form>
  );
}

export default function MfaForm({ status, destination }: MfaFormProp) {
  const router = useRouter();
  const mfa = useMfa();
  const [useBackupCode, setUseBackupCode] = useState(false);
  const enrolmentStarted = useRef(false);
  const continueToApp = () => router.replace(destination);
  const codeError = mfa.error?.fields.code ?? mfa.error?.message;
  const { startEnrolment } = mfa;

  // Setting up starts straight away, so the QR code is the first thing shown.
  useEffect(() => {
    if (status !== "ENROL" || enrolmentStarted.current) return;
    enrolmentStarted.current = true;
    startEnrolment();
  }, [status, startEnrolment]);

  if (mfa.backupCodes !== null) {
    const codes = mfa.backupCodes;
    const download = () => {
      const file = new Blob([codes.join("\n") + "\n"], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(file);
      link.download = "renttrace-backup-codes.txt";
      link.click();
      URL.revokeObjectURL(link.href);
    };

    return (
      <AuthCard
        tag={ADMIN_TAG}
        heading="Save your backup codes"
        message="Use one of these if you lose your phone. Each code works once. We won't show them again."
      >
        <ul className="grid grid-cols-2 gap-2">
          {codes.map((code) => (
            <li
              key={code}
              className="rounded-lg border border-default bg-subtle px-3 py-2 text-center font-mono text-body-sm"
            >
              {code}
            </li>
          ))}
        </ul>
        <div className="mt-5 grid grid-cols-2 gap-3">
          <Button
            variant="secondary"
            onClick={() => navigator.clipboard.writeText(codes.join("\n"))}
          >
            Copy
          </Button>
          <Button variant="secondary" onClick={download}>
            Download
          </Button>
        </div>
        <Button onClick={continueToApp} className="mt-3 w-full">
          I&apos;ve saved them, continue
        </Button>
      </AuthCard>
    );
  }

  if (status === "ENROL") {
    return (
      <AuthCard
        tag={ADMIN_TAG}
        heading="Set up two-step sign-in"
        message="Every Admin sign-in needs a code from an authenticator app. You only set this up once."
      >
        {mfa.enrolment ? (
          <form
            onSubmit={(event) => mfa.confirmEnrolment(readCode(event))}
            className="flex flex-col gap-5"
          >
            <div>
              <p className="text-body-sm font-semibold">
                1. Scan this QR code with your authenticator app
              </p>
              <div className="mt-3 inline-block rounded-lg border border-default bg-background p-3">
                <QRCode value={mfa.enrolment.provisioning_uri} size={148} />
              </div>
              <p className="mt-2 text-caption font-normal text-fg-secondary">
                Can&apos;t scan it? Enter this key:{" "}
                <span className="font-mono break-all text-fg-primary">
                  {groupInFours(mfa.enrolment.secret)}
                </span>
              </p>
            </div>
            <div>
              <p className="mb-3 text-body-sm font-semibold">
                2. Enter the 6-digit code it shows
              </p>
              <OtpInput name="code" label="6-digit code" error={codeError} />
            </div>
            <Button type="submit" pending={mfa.pending}>
              Turn on two-step sign-in
            </Button>
          </form>
        ) : mfa.error ? (
          <>
            <p role="alert" className="mb-4 text-body-sm text-error">
              {mfa.error.message}
            </p>
            <Button onClick={startEnrolment} pending={mfa.pending}>
              Try again
            </Button>
          </>
        ) : (
          <p role="status" className="text-body-sm text-fg-secondary">
            Preparing your QR code…
          </p>
        )}
        <BackToLogIn />
      </AuthCard>
    );
  }

  return (
    <AuthCard
      tag={ADMIN_TAG}
      heading="Enter your code"
      message={
        useBackupCode
          ? "Enter one of the backup codes you saved when you set up two-step sign-in."
          : "Open your authenticator app and enter the 6-digit code for RentTrace Admin."
      }
    >
      <form
        onSubmit={async (event) => {
          if (await mfa.verifyCode(readCode(event))) continueToApp();
        }}
        className="flex flex-col gap-4"
      >
        {useBackupCode ? (
          <TextInput
            label="Backup code"
            name="code"
            autoComplete="off"
            autoFocus
            required
            error={codeError}
          />
        ) : (
          <OtpInput
            name="code"
            label="6-digit code"
            autoFocus
            error={codeError}
          />
        )}
        <Button type="submit" pending={mfa.pending}>
          Verify
        </Button>
      </form>
      <button
        type="button"
        onClick={() => setUseBackupCode((value) => !value)}
        className={`mt-4 ${LINK_BUTTON_CLASS}`}
      >
        {useBackupCode ? "Use your authenticator app" : "Use a backup code"}
      </button>
      <BackToLogIn />
    </AuthCard>
  );
}
