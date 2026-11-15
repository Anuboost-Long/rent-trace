const dateFormat = new Intl.DateTimeFormat("en-GB", {
  dateStyle: "medium",
  timeZone: "UTC",
});

export const formatDate = (calendarDate: string | null) =>
  calendarDate ? dateFormat.format(new Date(calendarDate)) : "—";

const dayOnly = { dateStyle: "medium" } as const;
const dayAndTime = {
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZoneName: "short",
} as const;

export const formatInstant = (
  instant: string | null,
  { withTime, local }: Readonly<{ withTime?: boolean; local: boolean }>,
) => {
  if (!instant) return "—";
  const options = withTime ? dayAndTime : dayOnly;
  return new Intl.DateTimeFormat("en-GB", {
    ...options,
    ...(local ? {} : { timeZone: "UTC" }),
  }).format(new Date(instant));
};
