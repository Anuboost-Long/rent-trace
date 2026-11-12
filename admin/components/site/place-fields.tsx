"use client";
import ComboboxInput from "@/components/common/inputs/combobox-input";
import { AustralianStates } from "@/constants/locations";
import type { Place } from "@/types/listings/models";
import { useState } from "react";

type PlaceFieldsProp = Readonly<{
  places: Place[];
  defaultState?: string;
  defaultSuburb?: string;
}>;

const listingCount = (count: number) =>
  `${count} ${count === 1 ? "listing" : "listings"}`;

export default function PlaceFields({
  places,
  defaultState = "",
  defaultSuburb = "",
}: PlaceFieldsProp) {
  const [state, setState] = useState(defaultState);
  const [suburb, setSuburb] = useState(defaultSuburb);

  const states = [
    { value: "", label: "Anywhere" },
    ...AustralianStates.filter((option) =>
      places.some((place) => place.state === option.value),
    ),
  ];
  const suburbs = [
    { value: "", label: "Any suburb" },
    ...places
      .filter((place) => place.state === state)
      .map((place) => ({
        value: place.suburb,
        label: place.suburb,
        hint: listingCount(place.listings),
      })),
  ];

  return (
    <>
      <ComboboxInput
        label="State"
        name="state"
        value={state}
        options={states}
        placeholder="Anywhere"
        onSelect={(option) => {
          if (option.value === state) return;
          setState(option.value);
          setSuburb("");
        }}
      />
      <ComboboxInput
        key={state}
        label="Suburb"
        name="suburb"
        value={suburb}
        options={suburbs}
        disabled={!state}
        placeholder={state ? "Any suburb" : "Choose a state first"}
        emptyMessage="No listings here yet"
        onSelect={(option) => setSuburb(option.value)}
      />
    </>
  );
}
