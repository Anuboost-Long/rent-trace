import type { PropertySummary } from "@/types/properties/models";

type Address = Pick<
  PropertySummary,
  | "address_line_1"
  | "address_line_2"
  | "suburb"
  | "state"
  | "postcode"
  | "country"
>;

export const propertyTitle = (
  property: Pick<PropertySummary, "property_name" | "address_line_1">,
) => property.property_name ?? property.address_line_1;

export const formatAddress = (property: Address) =>
  [
    property.address_line_1,
    property.address_line_2,
    `${property.suburb} ${property.state} ${property.postcode}`,
    property.country,
  ]
    .filter(Boolean)
    .join(", ");

export const ownerName = (owner: { first_name: string; last_name: string }) =>
  `${owner.first_name} ${owner.last_name}`;
