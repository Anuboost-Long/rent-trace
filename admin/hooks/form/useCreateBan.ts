"use client";
import { handleCreateBan } from "@/api/services/bans/serve-action";
import { handleGetUsers } from "@/api/services/users/serve-action";
import type { ComboboxOption } from "@/components/common/inputs/combobox-input";
import { BanDurationDays } from "@/constants/security";
import type { CreatableBanType } from "@/types/security/models";
import { useRouter } from "next/navigation";
import { useState } from "react";
import useApiError from "@/hooks/useApiError";
import { toast } from "@/utils/toast";

const MS_PER_DAY = 86_400_000;

export const findPeople = async (query: string): Promise<ComboboxOption[]> => {
  const { data } = await handleGetUsers({ q: query, page_size: 8 });
  return (data?.results ?? []).map((person) => ({
    value: String(person.id),
    label: `${person.first_name} ${person.last_name}`,
    hint: person.email,
  }));
};

const useCreateBan = () => {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [type, setType] = useState<CreatableBanType>("EMAIL");
  const [value, setValue] = useState("");
  const [person, setPerson] = useState<ComboboxOption | null>(null);
  const [reason, setReason] = useState("");
  const [duration, setDuration] = useState("never");
  const [pending, setPending] = useState(false);
  const [error, setError] = useApiError();

  const close = () => {
    setOpen(false);
    setType("EMAIL");
    setValue("");
    setPerson(null);
    setReason("");
    setDuration("never");
    setError(null);
  };

  const days = BanDurationDays[duration];
  const target = type === "ACCOUNT" ? person : value.trim();
  const canSubmit = Boolean(target) && reason.trim() !== "";

  const submit = async () => {
    setPending(true);
    const { error } = await handleCreateBan({
      ban_type: type,
      reason: reason.trim(),
      ...(type === "ACCOUNT"
        ? { user_id: Number(person?.value) }
        : { value: value.trim() }),
      ...(days && {
        expires_at: new Date(Date.now() + days * MS_PER_DAY).toISOString(),
      }),
    });
    setPending(false);
    setError(error);
    if (error) return;
    close();
    toast.success("Ban created");
    router.refresh();
  };

  return {
    open,
    setOpen,
    type,
    setType,
    value,
    setValue,
    person,
    setPerson,
    reason,
    setReason,
    duration,
    setDuration,
    pending,
    error,
    canSubmit,
    submit,
    close,
  };
};

export default useCreateBan;
