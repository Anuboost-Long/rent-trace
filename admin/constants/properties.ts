import { Route } from "./web-routes";

export const PropertyTypeLabel: Record<string, string> = {
  HOUSE: "House",
  APARTMENT: "Apartment",
  TOWNHOUSE: "Townhouse",
  UNIT: "Unit",
  STUDIO: "Studio",
  ROOM: "Room",
  OTHER: "Other",
};

export const UnitTypeLabel: Record<string, string> = {
  WHOLE_PROPERTY: "Whole property",
  APARTMENT: "Apartment",
  ROOM: "Room",
  STUDIO: "Studio",
  OTHER: "Other",
};

export const PropertyStatusLabel: Record<string, string> = {
  ACTIVE: "Active",
  INACTIVE: "Inactive",
  UNDER_MAINTENANCE: "Under maintenance",
  ARCHIVED: "Archived",
};

export const OccupancyLabel: Record<string, string> = {
  VACANT: "Vacant",
  PARTIALLY_OCCUPIED: "Partly occupied",
  OCCUPIED: "Occupied",
  UNAVAILABLE: "Unavailable",
};

export const RentFrequencyLabel: Record<string, string> = {
  WEEKLY: "Weekly",
  FORTNIGHTLY: "Fortnightly",
  MONTHLY: "Monthly",
};

export const ListingStatusLabel: Record<string, string> = {
  DRAFT: "Draft",
  AVAILABLE: "Available",
  PARTIALLY_AVAILABLE: "Partly available",
  FULLY_OCCUPIED: "Fully occupied",
  UNLISTED: "Unlisted",
  SUSPENDED: "Suspended",
  ARCHIVED: "Archived",
};

export const ListingStatusHint: Record<string, string> = {
  DRAFT: "Not shown to the public yet.",
  AVAILABLE: "Shown to the public as available to rent.",
  PARTIALLY_AVAILABLE: "Shown to the public, with some units still available.",
  FULLY_OCCUPIED: "Hidden from the public because every unit is taken.",
  UNLISTED: "Hidden from the public. You can list it again any time.",
  SUSPENDED: "Hidden by an admin.",
  ARCHIVED: "Closed by an admin.",
};

export const PUBLIC_LISTING_STATUSES = ["AVAILABLE", "PARTIALLY_AVAILABLE"];

export const MANUAL_OCCUPANCY_STATUSES = [
  "VACANT",
  "PARTIALLY_OCCUPIED",
  "UNAVAILABLE",
];

export const labelOptions = (labels: Record<string, string>) =>
  Object.entries(labels).map(([value, label]) => ({ value, label }));

export const PropertyAccess = {
  admin: {
    create: "properties.admin_manage",
    update: "properties.admin_manage",
    publish: "properties.admin_manage",
  },
  landlord: {
    create: "properties.create",
    update: "properties.update",
    publish: "properties.publish",
  },
} as const;

export const PropertyRoutes = {
  admin: {
    list: Route.admin.properties,
    create: Route.admin.property_new,
    detail: Route.admin.property,
    edit: Route.admin.property_edit,
    unit: Route.admin.unit,
  },
  landlord: {
    list: Route.landlord.properties,
    create: Route.landlord.property_new,
    detail: Route.landlord.property,
    edit: Route.landlord.property_edit,
    unit: Route.landlord.unit,
  },
} as const;
