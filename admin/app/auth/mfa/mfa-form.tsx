"use client";
import { handleSignOut } from "@/api/services/auth/serve-action";
import AuthCard from "@/components/common/auth-card";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import useMfa from "@/hooks/form/useMfa";
import type { MfaStatus } from "@/types/auth/models";
import { useRouter } from "next/navigation";
import QRCode from "react-qr-code";

type MfaFormProp = Readonly<{ status: MfaStatus; destination: string }>;

export default function MfaForm({ status, destination }: MfaFormProp) {
  const router = useRouter();
  const mfa = useMfa();
  const continueToApp = () => router.replace(destination);

  const readCode = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    return String(new FormData(event.currentTarget).get("code")).trim();
  };

  const signOut = (
    <form action={handleSignOut} className="mt-4">
      <Button type="submit" variant="quiet" size="sm">
        Sign out
      </Button>
    </form>
  );

  const codeField = (
    <TextInput
      label="Verification code"
      name="code"
      inputMode="numeric"
      autoComplete="one-time-code"
      required
      error={mfa.error?.fields.code ?? mfa.error?.message}
    />
  );

  switch (true) {
    case mfa.backupCodes !== null:
      return (
        <AuthCard
          heading="Save your backup codes"
          message="Each code works once if you lose your authenticator app. You won't see them again."
        >
          <ul className="grid grid-cols-2 gap-2 font-mono">
            {mfa.backupCodes?.map((code) => (
              <li key={code}>{code}</li>
            ))}
          </ul>
          <div className="mt-6 flex gap-3">
            <Button
              variant="quiet"
              onClick={() =>
                navigator.clipboard.writeText(mfa.backupCodes!.join("\n"))
              }
            >
              Copy codes
            </Button>
            <Button onClick={continueToApp}>Continue</Button>
          </div>
        </AuthCard>
      );
    case mfa.enrolment !== null:
      return (
        <AuthCard
          heading="Scan the QR code"
          message="Scan it with an authenticator app, then enter the 6-digit code it shows."
        >
          <div className="mb-4 inline-block rounded-lg bg-white p-3">
            <QRCode value={mfa.enrolment!.provisioning_uri} size={160} />
          </div>
          <p className="mb-6 text-sm text-foreground/70">
            Can&apos;t scan? Enter this key instead:{" "}
            <span className="font-mono break-all">{mfa.enrolment!.secret}</span>
          </p>
          <form
            onSubmit={(event) => mfa.confirmEnrolment(readCode(event))}
            className="flex flex-col gap-4"
          >
            {codeField}
            <Button type="submit" pending={mfa.pending}>
              Confirm code
            </Button>
          </form>
          {signOut}
        </AuthCard>
      );
    case status === "ENROL":
      return (
        <AuthCard
          heading="Set up two-step verification"
          message="Admin accounts need a code from an authenticator app each time you sign in."
        >
          {mfa.error && (
            <p role="alert" className="mb-4 text-sm text-red-600">
              {mfa.error.message}
            </p>
          )}
          <Button onClick={mfa.startEnrolment} pending={mfa.pending}>
            Set up authenticator app
          </Button>
          {signOut}
        </AuthCard>
      );
    default:
      return (
        <AuthCard
          heading="Enter your verification code"
          message="Use the 6-digit code from your authenticator app, or a backup code."
        >
          <form
            onSubmit={async (event) => {
              if (await mfa.verifyCode(readCode(event))) continueToApp();
            }}
            className="flex flex-col gap-4"
          >
            {codeField}
            <Button type="submit" pending={mfa.pending}>
              Verify
            </Button>
          </form>
          {signOut}
        </AuthCard>
      );
  }
}
