"use client";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import useUpdateProfile from "@/hooks/form/useUpdateProfile";
import type { Me } from "@/types/auth/models";
import { Pencil } from "lucide-react";
import { useState } from "react";

type ProfileSectionProp = Readonly<{ user: Me }>;

export default function ProfileSection({ user }: ProfileSectionProp) {
  const [editing, setEditing] = useState(false);
  const { pending, error, clearError, save } = useUpdateProfile(() =>
    setEditing(false),
  );

  const stopEditing = () => {
    setEditing(false);
    clearError();
  };

  return (
    <section aria-labelledby="profile-heading">
      <div className="flex items-center justify-between gap-4">
        <h2 id="profile-heading" className="text-lg font-semibold">
          Profile
        </h2>
        {!editing && (
          <Button
            variant="quiet"
            size="sm"
            className="gap-2"
            onClick={() => setEditing(true)}
          >
            <Pencil aria-hidden className="size-4" />
            Edit
          </Button>
        )}
      </div>

      {editing ? (
        <form
          onSubmit={(event) => {
            event.preventDefault();
            const form = new FormData(event.currentTarget);
            save({
              first_name: String(form.get("first_name")),
              last_name: String(form.get("last_name")),
              phone_number: String(form.get("phone_number") ?? ""),
            });
          }}
          className="mt-3 flex flex-col gap-4 rounded-xl border border-foreground/15 p-4"
        >
          <div className="grid gap-4 sm:grid-cols-2">
            <TextInput
              label="First name"
              name="first_name"
              autoComplete="given-name"
              defaultValue={user.first_name}
              required
              error={error?.fields.first_name}
            />
            <TextInput
              label="Last name"
              name="last_name"
              autoComplete="family-name"
              defaultValue={user.last_name}
              required
              error={error?.fields.last_name}
            />
          </div>
          <TextInput
            label="Phone number (optional)"
            name="phone_number"
            type="tel"
            autoComplete="tel"
            defaultValue={user.phone_number ?? ""}
            error={error?.fields.phone_number}
          />
          <p className="text-sm text-foreground/70">
            Your email is how you sign in, so it can&apos;t be changed here.
          </p>
          {error && Object.keys(error.fields).length === 0 && (
            <p role="alert" className="text-sm text-red-600">
              {error.message}
            </p>
          )}
          <div className="flex gap-3">
            <Button type="submit" pending={pending}>
              {pending ? "Saving…" : "Save changes"}
            </Button>
            <Button variant="quiet" onClick={stopEditing} disabled={pending}>
              Cancel
            </Button>
          </div>
        </form>
      ) : (
        <dl className="mt-3 divide-y divide-foreground/15 rounded-xl border border-foreground/15">
          <Row label="Name">
            {user.first_name} {user.last_name}
          </Row>
          <Row label="Phone number">{user.phone_number ?? "Not added"}</Row>
        </dl>
      )}
    </section>
  );
}

function Row({
  label,
  children,
}: Readonly<{ label: string; children: React.ReactNode }>) {
  return (
    <div className="grid gap-1 p-4 sm:grid-cols-[12rem_1fr]">
      <dt className="text-sm text-foreground/70">{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}
