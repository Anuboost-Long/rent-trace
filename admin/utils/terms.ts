import type { MoneyTerms } from "@/types/tenancies/models";

import { formatMoney, formatRent } from "./rent";

export const rentText = (terms: MoneyTerms) =>
  terms.rent_amount && terms.rent_frequency
    ? formatRent(terms.rent_amount, terms.rent_frequency)
    : "Not set";

export const bondText = (terms: MoneyTerms) =>
  terms.bond_amount ? formatMoney(terms.bond_amount) : "Not set";

export const changedRows = (before: MoneyTerms, after: MoneyTerms) =>
  [
    { label: "Rent", before: rentText(before), after: rentText(after) },
    { label: "Bond", before: bondText(before), after: bondText(after) },
  ].filter((row) => row.before !== row.after);
