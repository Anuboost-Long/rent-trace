const PER: Record<string, string> = {
  WEEKLY: "week",
  FORTNIGHTLY: "fortnight",
  MONTHLY: "month",
};

const dollars = new Intl.NumberFormat("en-AU", {
  style: "currency",
  currency: "AUD",
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

export const formatRent = (amount: string, frequency: string) =>
  `${dollars.format(Number(amount))} per ${PER[frequency] ?? "week"}`;

export const formatMoney = (amount: string) => dollars.format(Number(amount));
