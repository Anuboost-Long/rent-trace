import assert from "node:assert/strict";
import { test } from "node:test";
import { formatDate, formatInstant } from "./format-date.ts";

const lateEveningUtc = "2026-11-13T15:56:56Z";

test("a calendar date is shown as stored", () => {
  assert.equal(formatDate("2026-12-01"), "1 Dec 2026");
});

test("a missing value shows a dash", () => {
  assert.equal(formatDate(null), "—");
  assert.equal(formatInstant(null, { local: true }), "—");
});

test("the server-side first paint of a timestamp is in UTC", () => {
  assert.equal(
    formatInstant(lateEveningUtc, { withTime: true, local: false }),
    "13 Nov 2026, 15:56 UTC",
  );
});

test("a timestamp crosses the day boundary in a zone ahead of UTC", () => {
  const original = process.env.TZ;
  process.env.TZ = "Australia/Sydney";
  try {
    assert.equal(formatInstant(lateEveningUtc, { local: true }), "14 Nov 2026");
    assert.equal(formatDate("2026-11-13"), "13 Nov 2026");
  } finally {
    process.env.TZ = original;
  }
});
