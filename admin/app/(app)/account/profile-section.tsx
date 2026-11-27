"use client";
import Avatar from "@/components/common/avatar";
import Button from "@/components/common/button";
import TextInput from "@/components/common/inputs/text-input";
import useUpdateProfile, {
  type PictureChange,
} from "@/hooks/form/useUpdateProfile";
import type { Me } from "@/types/auth/models";
import { ImagePlus, Pencil, Trash2 } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

const MAX_PICTURE_BYTES = 10_000_000;
const PICTURE_TYPES = ["image/jpeg", "image/png"];

type ProfileSectionProp = Readonly<{ user: Me }>;

export default function ProfileSection({ user }: ProfileSectionProp) {
  const [editing, setEditing] = useState(false);
  const [newFile, setNewFile] = useState<File | null>(null);
  const [removing, setRemoving] = useState(false);
  const [pictureProblem, setPictureProblem] = useState<string | null>(null);
  const picker = useRef<HTMLInputElement>(null);
  const preview = useMemo(
    () => (newFile ? URL.createObjectURL(newFile) : null),
    [newFile],
  );
  useEffect(
    () => () => {
      if (preview) URL.revokeObjectURL(preview);
    },
    [preview],
  );

  const { pending, error, clearError, save } = useUpdateProfile(() => {
    setEditing(false);
    setNewFile(null);
    setRemoving(false);
  });

  const stopEditing = () => {
    setEditing(false);
    setNewFile(null);
    setRemoving(false);
    setPictureProblem(null);
    clearError();
  };

  const choose = (file: File | undefined) => {
    if (!file) return;
    if (!PICTURE_TYPES.includes(file.type)) {
      setPictureProblem("Choose a JPEG or PNG image.");
    } else if (file.size > MAX_PICTURE_BYTES) {
      setPictureProblem("The picture must be 10 MB or smaller.");
    } else {
      setPictureProblem(null);
      setNewFile(file);
      setRemoving(false);
    }
  };

  const pictureChange: PictureChange = newFile
    ? { file: newFile }
    : removing
      ? { remove: true }
      : null;
  const showsPicture =
    preview !== null || (user.picture_id !== null && !removing);

  return (
    <section aria-labelledby="profile-heading">
      <div className="flex items-center justify-between gap-4">
        <h2 id="profile-heading" className="text-section">
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
            save(
              {
                first_name: String(form.get("first_name")),
                last_name: String(form.get("last_name")),
                phone_number: String(form.get("phone_number") ?? ""),
              },
              pictureChange,
            );
          }}
          className="mt-3 flex flex-col gap-4 rounded-xl border border-default p-4"
        >
          <div className="flex flex-wrap items-center gap-4">
            {preview ? (
              // eslint-disable-next-line @next/next/no-img-element -- a local preview, not a served image
              <img
                src={preview}
                alt="New profile picture"
                className="size-16 rounded-full object-cover"
              />
            ) : (
              <Avatar
                firstName={user.first_name}
                lastName={user.last_name}
                userId={user.id}
                pictureId={removing ? null : user.picture_id}
                className="size-16 text-section"
              />
            )}
            <div>
              <div className="flex flex-wrap gap-2">
                <input
                  ref={picker}
                  type="file"
                  accept="image/jpeg,image/png"
                  hidden
                  onChange={(event) => {
                    choose(event.target.files?.[0]);
                    event.target.value = "";
                  }}
                />
                <Button
                  variant="quiet"
                  size="sm"
                  className="gap-2"
                  onClick={() => picker.current?.click()}
                  disabled={pending}
                >
                  <ImagePlus aria-hidden className="size-4" />
                  {showsPicture ? "Change photo" : "Add photo"}
                </Button>
                {showsPicture && (
                  <Button
                    variant="quiet"
                    size="sm"
                    className="gap-2"
                    onClick={() => {
                      setNewFile(null);
                      setRemoving(true);
                    }}
                    disabled={pending}
                  >
                    <Trash2 aria-hidden className="size-4" />
                    Remove
                  </Button>
                )}
              </div>
              <p className="mt-1 text-caption text-fg-tertiary">
                JPEG or PNG, up to 10 MB. It changes when you save.
              </p>
              {pictureProblem && (
                <p role="alert" className="mt-1 text-sm text-error">
                  {pictureProblem}
                </p>
              )}
            </div>
          </div>
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
          <p className="text-sm text-fg-secondary">
            Your email is how you sign in, so it can&apos;t be changed here.
          </p>
          {error && Object.keys(error.fields).length === 0 && (
            <p role="alert" className="text-sm text-error">
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
        <dl className="mt-3 divide-y divide-default rounded-xl border border-default">
          <Row label="Photo">
            <Avatar
              firstName={user.first_name}
              lastName={user.last_name}
              userId={user.id}
              pictureId={user.picture_id}
              className="size-12 text-body-sm"
            />
          </Row>
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
      <dt className="text-sm text-fg-secondary">{label}</dt>
      <dd>{children}</dd>
    </div>
  );
}
