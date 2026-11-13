"use client";
import CheckInput from "@/components/common/inputs/check-input";
import TextArea from "@/components/common/inputs/text-area-input";
import type { PropertySummary } from "@/types/properties/models";
import type { ProviderProperty } from "@/types/providers/models";
import { useState } from "react";

type PropertyLinkFieldsProp = Readonly<{
  property: PropertySummary;
  link?: ProviderProperty;
}>;

export default function PropertyLinkFields({
  property,
  link,
}: PropertyLinkFieldsProp) {
  const [linked, setLinked] = useState(Boolean(link));

  return (
    <li className="flex flex-col gap-3 p-4">
      <CheckInput
        label={property.property_name ?? property.address_line_1}
        name={`linked_${property.id}`}
        checked={linked}
        onChange={(event) => setLinked(event.target.checked)}
      />
      {linked && (
        <div className="flex flex-col gap-3 pl-6">
          <CheckInput
            label="Preferred for this property"
            name={`preferred_${property.id}`}
            defaultChecked={link?.is_recommended}
          />
          <TextArea
            label="Contract notes"
            name={`notes_${property.id}`}
            rows={2}
            defaultValue={link?.contract_notes ?? ""}
          />
        </div>
      )}
    </li>
  );
}
