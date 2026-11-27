export type Field =
  | {
      kind: "text" | "textarea" | "number" | "date" | "datetime" | "numbers";
      name: string;
      required?: boolean;
      value?: string | number;
      hint?: string;
    }
  | { kind: "checkbox"; name: string; value?: boolean }
  | { kind: "select"; name: string; options: string[]; required?: boolean }
  | { kind: "file"; name: string; required?: boolean }
  | { kind: "key"; name: "idempotency_key" };

export type Call = {
  title: string;
  method: "GET" | "POST";
  path: string;
  fields?: Field[];
  note?: string;
};

const text = (name: string, required = false): Field => ({
  kind: "text",
  name,
  required,
});
const area = (name: string, required = false): Field => ({
  kind: "textarea",
  name,
  required,
});
const key: Field = { kind: "key", name: "idempotency_key" };
const reason: Field = area("reason", true);

const DOCUMENT_TYPES = [
  "TENANCY_AGREEMENT",
  "CONDITION_REPORT",
  "NOTICE",
  "RECEIPT",
  "OTHER",
];
const STATUSES = [
  "PENDING_REVIEW",
  "APPROVED",
  "REJECTED",
  "STALE",
  "CANCELLED",
];

const queue = (title: string, path: string): Call[] => [
  {
    title: `${title}: list`,
    method: "GET",
    path,
    fields: [{ kind: "select", name: "status", options: ["", ...STATUSES] }],
  },
  {
    title: `${title}: approve`,
    method: "POST",
    path: `${path}{id}/approve/`,
    fields: [key, reason],
  },
  {
    title: `${title}: reject`,
    method: "POST",
    path: `${path}{id}/reject/`,
    fields: [key, reason],
  },
];

const correctionFields: Field[] = [
  { kind: "number", name: "record_id", required: true },
  text("title"),
  area("what_is_incorrect", true),
  area("proposed_replacement", true),
  area("why_change_needed", true),
];
const removalFields: Field[] = [
  { kind: "numbers", name: "record_ids", required: true, hint: "1,2,3" },
  reason,
  { kind: "checkbox", name: "include_descendants", value: true },
];
const reportFields: Field[] = [
  text("title", true),
  area("description"),
  { kind: "datetime", name: "observed_at", required: true },
];
const respondFields: Field[] = [
  area("message", true),
  text("title"),
  area("description"),
];
const versionFields: Field[] = [
  text("title"),
  area("description"),
  { kind: "date", name: "document_date" },
  { kind: "file", name: "file", required: true },
];

export const tenantCalls = (tenancyId: string): Call[] => {
  const base = `tenant/tenancies/${tenancyId}`;
  return [
    {
      title: "Reports: list",
      method: "GET",
      path: `${base}/condition-evidence/`,
    },
    {
      title: "Reports: add",
      method: "POST",
      path: `${base}/condition-evidence/`,
      fields: reportFields,
    },
    {
      title: "Reports: add a photo",
      method: "POST",
      path: `${base}/condition-evidence/{request_id}/photos/`,
      fields: [{ kind: "file", name: "file", required: true }],
    },
    {
      title: "Reports: withdraw",
      method: "POST",
      path: `${base}/condition-evidence/{request_id}/cancel/`,
    },
    {
      title: "Reports: answer a question",
      method: "POST",
      path: `${base}/condition-evidence/{request_id}/respond/`,
      fields: respondFields,
    },
    {
      title: "Reports: ask an admin to decide",
      method: "POST",
      path: `${base}/condition-evidence/{request_id}/escalate/`,
      fields: [reason],
    },
    {
      title: "Corrections: list",
      method: "GET",
      path: `${base}/condition-corrections/`,
    },
    {
      title: "Corrections: ask",
      method: "POST",
      path: `${base}/condition-corrections/`,
      fields: correctionFields,
    },
    {
      title: "Corrections: withdraw",
      method: "POST",
      path: `${base}/condition-corrections/{request_id}/cancel/`,
    },
    {
      title: "Removals: list",
      method: "GET",
      path: `${base}/removal-requests/`,
    },
    {
      title: "Removals: ask",
      method: "POST",
      path: `${base}/removal-requests/`,
      fields: removalFields,
    },
    {
      title: "Removals: withdraw",
      method: "POST",
      path: `${base}/removal-requests/{request_id}/cancel/`,
    },
    { title: "Documents: list", method: "GET", path: `${base}/documents/` },
    {
      title: "Documents: one",
      method: "GET",
      path: `${base}/documents/{document_id}/`,
    },
    {
      title: "Documents: confirm a version",
      method: "POST",
      path: `${base}/documents/versions/{version_id}/confirm/`,
      fields: [key],
    },
    {
      title: "Documents: flag a version",
      method: "POST",
      path: `${base}/documents/versions/{version_id}/flag/`,
      fields: [key, reason],
    },
  ];
};

export const landlordCalls = (unitId: string): Call[] => {
  const unit: Field = {
    kind: "number",
    name: "unit_id",
    value: unitId,
    required: true,
  };
  return [
    {
      title: "Reports: list",
      method: "GET",
      path: "landlord/condition-evidence/",
      fields: [unit],
    },
    {
      title: "Reports: approve",
      method: "POST",
      path: "landlord/condition-evidence/{id}/approve/",
      fields: [key],
    },
    {
      title: "Reports: reject",
      method: "POST",
      path: "landlord/condition-evidence/{id}/reject/",
      fields: [key, reason],
    },
    {
      title: "Reports: ask for more information",
      method: "POST",
      path: "landlord/condition-evidence/{id}/request-information/",
      fields: [key, reason],
    },
    {
      title: "Reports: ask an admin to decide",
      method: "POST",
      path: "landlord/condition-evidence/{id}/escalate/",
      fields: [reason],
    },
    {
      title: "Corrections: list",
      method: "GET",
      path: "landlord/condition-corrections/",
      fields: [unit],
    },
    {
      title: "Corrections: ask",
      method: "POST",
      path: "landlord/condition-corrections/",
      fields: correctionFields,
    },
    {
      title: "Corrections: withdraw",
      method: "POST",
      path: "landlord/condition-corrections/{request_id}/cancel/",
    },
    {
      title: "Removals: list",
      method: "GET",
      path: "landlord/removal-requests/",
      fields: [unit],
    },
    {
      title: "Removals: ask",
      method: "POST",
      path: "landlord/removal-requests/",
      fields: removalFields,
    },
    {
      title: "Removals: withdraw",
      method: "POST",
      path: "landlord/removal-requests/{request_id}/cancel/",
    },
    {
      title: "Documents: list",
      method: "GET",
      path: "landlord/documents/",
      fields: [unit],
    },
    {
      title: "Documents: one",
      method: "GET",
      path: "landlord/documents/{document_id}/",
    },
    {
      title: "Documents: publish",
      method: "POST",
      path: "landlord/documents/",
      fields: [
        unit,
        {
          kind: "select",
          name: "document_type",
          options: DOCUMENT_TYPES,
          required: true,
        },
        text("title", true),
        area("description"),
        { kind: "date", name: "document_date" },
        { kind: "number", name: "tenancy_id" },
        { kind: "number", name: "maintenance_issue_id" },
        { kind: "file", name: "file", required: true },
      ],
    },
    {
      title: "Documents: add a version",
      method: "POST",
      path: "landlord/documents/{document_id}/versions/",
      fields: versionFields,
    },
  ];
};

export const adminCalls = (unitId: string): Call[] => {
  const unit: Field = {
    kind: "number",
    name: "unit_id",
    value: unitId,
    required: true,
  };
  return [
    ...queue("Review cases", "admin/review-cases/"),
    ...queue("Corrections", "admin/condition-corrections/"),
    ...queue("Removals", "admin/removal-requests/"),
    {
      title: "Documents: list",
      method: "GET",
      path: "admin/documents/",
      fields: [unit],
    },
    {
      title: "Documents: one",
      method: "GET",
      path: "admin/documents/{document_id}/",
    },
    {
      title: "Reports on a unit: list",
      method: "GET",
      path: "admin/condition-evidence/",
      fields: [unit],
    },
    {
      title: "Super admin, as the owner: approve",
      method: "POST",
      path: "admin/condition-evidence/{id}/approve/",
      fields: [key],
    },
    {
      title: "Super admin, as the owner: reject",
      method: "POST",
      path: "admin/condition-evidence/{id}/reject/",
      fields: [key, reason],
    },
    {
      title: "Super admin, as the owner: ask for more information",
      method: "POST",
      path: "admin/condition-evidence/{id}/request-information/",
      fields: [key, reason],
    },
    {
      title: "Super admin, as the tenant: withdraw",
      method: "POST",
      path: "admin/condition-evidence/{id}/cancel/",
    },
    {
      title: "Super admin, as the tenant: answer a question",
      method: "POST",
      path: "admin/condition-evidence/{id}/respond/",
      fields: respondFields,
    },
  ];
};
