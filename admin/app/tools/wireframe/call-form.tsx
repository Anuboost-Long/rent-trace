"use client";
import { useEffect, useRef, useState } from "react";

import { callJson, callUpload, type CallResult } from "./actions";
import type { Call, Field } from "./spec";

const placeholders = (path: string) =>
  [...path.matchAll(/\{(\w+)\}/g)].map((match) => match[1]);

const fieldsOf = (call: Call): Field[] => [
  ...placeholders(call.path).map((name): Field => ({
    kind: "number",
    name,
    required: true,
  })),
  ...(call.fields ?? []),
];

const readValue = (field: Field, form: FormData): unknown => {
  const raw = form.get(field.name);
  switch (field.kind) {
    case "key":
      return crypto.randomUUID();
    case "checkbox":
      return raw === "on";
    case "number":
      return raw === "" || raw === null ? undefined : Number(raw);
    case "numbers":
      return String(raw ?? "")
        .split(",")
        .map((part) => part.trim())
        .filter(Boolean)
        .map(Number);
    case "datetime":
      return raw ? `${String(raw)}:00Z` : undefined;
    default:
      return raw === "" || raw === null ? undefined : raw;
  }
};

const input = (field: Field) => {
  const common = { name: field.name, id: undefined };
  switch (field.kind) {
    case "key":
      return null;
    case "textarea":
      return (
        <textarea
          {...common}
          required={field.required}
          defaultValue={field.value}
        />
      );
    case "checkbox":
      return <input {...common} type="checkbox" defaultChecked={field.value} />;
    case "select":
      return (
        <select {...common} required={field.required}>
          {field.options.map((option) => (
            <option key={option} value={option}>
              {option || "(any)"}
            </option>
          ))}
        </select>
      );
    case "file":
      return <input {...common} type="file" required={field.required} />;
    case "datetime":
      return (
        <input {...common} type="datetime-local" required={field.required} />
      );
    case "number":
      return (
        <input
          {...common}
          type="number"
          required={field.required}
          defaultValue={field.value}
        />
      );
    case "date":
      return <input {...common} type="date" defaultValue={field.value} />;
    default:
      return (
        <input
          {...common}
          type="text"
          required={field.required}
          defaultValue={field.value}
          placeholder={field.kind === "numbers" ? field.hint : undefined}
        />
      );
  }
};

const submit = async (call: Call, fields: Field[], form: HTMLFormElement) => {
  const data = new FormData(form);
  let path = call.path;
  for (const name of placeholders(call.path)) {
    path = path.replace(`{${name}}`, String(data.get(name)));
  }
  const own = fields.filter(
    (field) => !placeholders(call.path).includes(field.name),
  );
  if (own.some((field) => field.kind === "file")) {
    const upload = new FormData();
    for (const field of own) {
      const value =
        field.kind === "file" ? data.get(field.name) : readValue(field, data);
      if (value !== undefined && value !== "")
        upload.set(field.name, value as string | Blob);
    }
    return callUpload(path, upload);
  }
  const values = Object.fromEntries(
    own.map((field) => [field.name, readValue(field, data)]),
  );
  return call.method === "GET"
    ? callJson({
        method: "GET",
        path,
        query: Object.fromEntries(
          Object.entries(values).filter(
            ([, value]) => value !== undefined && value !== "",
          ),
        ) as Record<string, string | number>,
      })
    : callJson({ method: "POST", path, json: values });
};

export default function CallForm({ call }: Readonly<{ call: Call }>) {
  const formRef = useRef<HTMLFormElement>(null);
  const [result, setResult] = useState<CallResult | null>(null);
  const [pending, setPending] = useState(false);
  const fields = fieldsOf(call);
  const isAutorun =
    call.method === "GET" &&
    placeholders(call.path).length === 0 &&
    fields.every(
      (field) =>
        !("required" in field && field.required) ||
        ("value" in field && field.value !== undefined),
    );

  const run = async () => {
    if (!formRef.current) return;
    setPending(true);
    setResult(await submit(call, fields, formRef.current));
    setPending(false);
  };

  useEffect(() => {
    if (isAutorun) void run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <details open={call.method === "GET"}>
      <summary>
        {call.method} {call.title}
      </summary>
      <form
        ref={formRef}
        onSubmit={(event) => {
          event.preventDefault();
          void run();
        }}
      >
        <p>
          <code>{call.path}</code>
        </p>
        {fields.map((field) =>
          field.kind === "key" ? null : (
            <p key={field.name}>
              <label>
                {field.name}
                {"required" in field && field.required ? " *" : ""}{" "}
                {input(field)}
              </label>
            </p>
          ),
        )}
        <button type="submit" disabled={pending}>
          {call.method === "GET" ? "Load" : "Send"}
        </button>
      </form>
      {result && (
        <pre>
          {result.status === 200 ? "OK" : `Error ${result.status}`}
          {"\n"}
          {typeof result.body === "string"
            ? result.body
            : JSON.stringify(result.body, null, 2)}
        </pre>
      )}
    </details>
  );
}

export function DownloadForm({
  role,
  tenancy,
}: Readonly<{ role: "tenant" | "landlord" | "admin"; tenancy?: string }>) {
  return (
    <details>
      <summary>GET Download a photo or document file</summary>
      <form action="/tools/wireframe/download" method="get" target="_blank">
        <input type="hidden" name="role" value={role} />
        {tenancy && <input type="hidden" name="tenancy" value={tenancy} />}
        <p>
          <label>
            kind{" "}
            <select name="kind">
              <option value="photo">photo (report)</option>
              <option value="document">document</option>
            </select>
          </label>
        </p>
        <p>
          <label>
            file id * <input type="number" name="file" required />
          </label>
        </p>
        <button type="submit">Download</button>
      </form>
    </details>
  );
}
