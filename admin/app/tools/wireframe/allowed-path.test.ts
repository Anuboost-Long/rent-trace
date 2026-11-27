import assert from "node:assert/strict";
import { test } from "node:test";

import { isAllowedPath } from "./allowed-path.ts";

test("reviews and documents routes are allowed", () => {
  for (const path of [
    "tenant/tenancies/6/condition-evidence/",
    "tenant/tenancies/6/documents/versions/3/confirm/",
    "landlord/condition-corrections/4/cancel/",
    "landlord/documents/",
    "admin/review-cases/2/approve/",
    "admin/condition-evidence/9/respond/",
    "auth/profile/picture/",
  ]) {
    assert.equal(isAllowedPath(path), true, path);
  }
});

test("everything else is refused", () => {
  for (const path of [
    "auth/sign-in/",
    "auth/profile/",
    "auth/profile/picture/x/",
    "admin/users/",
    "landlord/properties/",
    "tenant/tenancies/x/documents/",
    "tenant/tenancies/6/invitations/",
    "landlord/documents/../../auth/me/",
    "admin/documents/?x=1",
    "https://example.com/",
    "",
  ]) {
    assert.equal(isAllowedPath(path), false, path);
  }
});
