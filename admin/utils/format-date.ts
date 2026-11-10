const dateFormat = new Intl.DateTimeFormat("en-GB", {
  dateStyle: "medium",
  timeZone: "UTC",
});

export const formatDate = (iso: string | null) =>
  iso ? dateFormat.format(new Date(iso)) : "—";

const dateTimeFormat = new Intl.DateTimeFormat("en-GB", {
  dateStyle: "medium",
  timeStyle: "short",
  timeZone: "UTC",
});

export const formatDateTime = (iso: string | null) =>
  iso ? `${dateTimeFormat.format(new Date(iso))} UTC` : "—";
