const MS_PER_DAY = 86_400_000;

export const WEEKDAYS = [
  { short: "Mo", long: "Monday" },
  { short: "Tu", long: "Tuesday" },
  { short: "We", long: "Wednesday" },
  { short: "Th", long: "Thursday" },
  { short: "Fr", long: "Friday" },
  { short: "Sa", long: "Saturday" },
  { short: "Su", long: "Sunday" },
];

export type CalendarDay = { iso: string; day: number; inMonth: boolean };

const utcTime = (iso: string) => Date.parse(`${iso}T00:00:00Z`);

const isoOf = (time: number) => new Date(time).toISOString().slice(0, 10);

export const todayIso = () => isoOf(Date.now());

export const addDays = (iso: string, days: number) =>
  isoOf(utcTime(iso) + days * MS_PER_DAY);

export const addMonths = (iso: string, months: number) => {
  const date = new Date(utcTime(iso));
  const target = new Date(
    Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + months, 1),
  );
  const lastDay = new Date(
    Date.UTC(target.getUTCFullYear(), target.getUTCMonth() + 1, 0),
  ).getUTCDate();
  target.setUTCDate(Math.min(date.getUTCDate(), lastDay));
  return isoOf(target.getTime());
};

export const monthStart = (iso: string) => `${iso.slice(0, 7)}-01`;

export const monthWeeks = (iso: string): CalendarDay[][] => {
  const first = monthStart(iso);
  const mondayOffset = (new Date(utcTime(first)).getUTCDay() + 6) % 7;
  const gridStart = addDays(first, -mondayOffset);
  return Array.from({ length: 6 }, (_, week) =>
    Array.from({ length: 7 }, (_, weekday) => {
      const cell = addDays(gridStart, week * 7 + weekday);
      return {
        iso: cell,
        day: Number(cell.slice(8)),
        inMonth: cell.slice(0, 7) === first.slice(0, 7),
      };
    }),
  );
};

const monthFormat = new Intl.DateTimeFormat("en-GB", {
  month: "long",
  year: "numeric",
  timeZone: "UTC",
});

export const monthLabel = (iso: string) =>
  monthFormat.format(new Date(utcTime(iso)));

const longDateFormat = new Intl.DateTimeFormat("en-GB", {
  dateStyle: "full",
  timeZone: "UTC",
});

export const longDate = (iso: string) =>
  longDateFormat.format(new Date(utcTime(iso)));
