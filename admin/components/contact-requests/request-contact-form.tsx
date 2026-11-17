"use client";
import Button from "@/components/common/button";
import SelectInput from "@/components/common/inputs/select-input";
import TextAreaInput from "@/components/common/inputs/text-area-input";
import useSendContactRequest from "@/hooks/form/useSendContactRequest";
import { useState } from "react";

type RequestContactFormProp = Readonly<{
  listingId: number;
  units: { id: number; name: string }[];
}>;

const ANY_UNIT = "";

export default function RequestContactForm({
  listingId,
  units,
}: RequestContactFormProp) {
  const { pending, error, send } = useSendContactRequest();
  const [message, setMessage] = useState("");
  const [unitId, setUnitId] = useState(ANY_UNIT);

  return (
    <form
      className="mt-4 space-y-4"
      onSubmit={(event) => {
        event.preventDefault();
        send({
          listing_id: listingId,
          unit_id: unitId === ANY_UNIT ? null : Number(unitId),
          message: message.trim(),
        });
      }}
    >
      {units.length > 1 && (
        <SelectInput
          label="Which unit?"
          name="unit_id"
          value={unitId}
          onValueChange={setUnitId}
          error={error?.fields.unit_id}
          options={[
            { value: ANY_UNIT, label: "Any unit" },
            ...units.map((unit) => ({
              value: String(unit.id),
              label: unit.name,
            })),
          ]}
        />
      )}
      <TextAreaInput
        label="Message to the landlord"
        name="message"
        rows={4}
        maxLength={1000}
        required
        placeholder="Introduce yourself and say when you'd like to move in."
        value={message}
        onChange={(event) => setMessage(event.target.value)}
        error={error?.fields.message}
      />
      {error && !error.fields.message && !error.fields.unit_id && (
        <p role="alert" className="text-sm text-red-600">
          {error.fields.listing_id ?? error.message}
        </p>
      )}
      <Button
        type="submit"
        className="w-full"
        pending={pending}
        disabled={message.trim() === ""}
      >
        Request contact
      </Button>
      <p className="text-xs text-foreground/60">
        The landlord sees your name and message. If they accept, they also see
        your email and phone, and you see theirs.
      </p>
    </form>
  );
}
