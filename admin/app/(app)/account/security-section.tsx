"use client";
import Button from "@/components/common/button";
import CheckInput from "@/components/common/inputs/check-input";
import TextInput from "@/components/common/inputs/text-input";
import useChangePassword from "@/hooks/form/useChangePassword";
import type { Me } from "@/types/auth/models";

type SecuritySectionProp = Readonly<{ user: Me }>;

export default function SecuritySection({ user }: SecuritySectionProp) {
  const { pending, error, notice, change } = useChangePassword();
  const hasPassword = user.auth_method !== "GOOGLE";
  const hasAuthenticator = user.mfa_status === "VERIFIED";

  return (
    <section aria-labelledby="security-heading">
      <h2 id="security-heading" className="text-lg font-semibold">
        Security
      </h2>

      {hasPassword ? (
        <form
          onSubmit={async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const data = new FormData(form);
            const changed = await change({
              current_password: String(data.get("current_password")),
              new_password: String(data.get("new_password")),
              sign_out_other_devices:
                data.get("sign_out_other_devices") === "on",
              ...(hasAuthenticator && {
                code: String(data.get("code")).trim(),
              }),
            });
            if (changed) form.reset();
          }}
          className="mt-3 flex flex-col gap-4 rounded-xl border border-default p-4"
        >
          <h3 className="text-sm font-semibold">Change password</h3>
          <TextInput
            label="Current password"
            name="current_password"
            type="password"
            autoComplete="current-password"
            required
            error={error?.fields.current_password}
          />
          <TextInput
            label="New password"
            name="new_password"
            type="password"
            autoComplete="new-password"
            required
            error={error?.fields.new_password}
          />
          {hasAuthenticator && (
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
            name="sign_out_other_devices"
            label="Sign me out of my other devices"
          />
          {error && Object.keys(error.fields).length === 0 && (
            <p role="alert" className="text-sm text-error">
              {error.message}
            </p>
          )}
          {notice && <p role="status">{notice}</p>}
          <Button type="submit" pending={pending} className="self-start">
            {pending ? "Changing password…" : "Change password"}
          </Button>
        </form>
      ) : (
        <p className="mt-3 rounded-xl border border-default p-4 text-fg-secondary">
          You sign in with Google, so there is no RentTrace password to change.
          Manage your password in your Google account.
        </p>
      )}

      {user.is_admin && (
        <p className="mt-3 rounded-xl border border-default p-4 text-fg-secondary">
          Two-step verification is required for admin accounts and is on for
          this account.
        </p>
      )}
    </section>
  );
}
