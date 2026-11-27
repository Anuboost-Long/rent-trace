"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

const ROLES = [
  { role: "tenant", label: "Tenant (tenancy id)" },
  { role: "landlord", label: "Landlord (unit id)" },
  { role: "admin", label: "Admin (unit id, optional)" },
] as const;

export default function GoForm() {
  const router = useRouter();
  const [ids, setIds] = useState<Record<string, string>>({});

  return (
    <ul>
      {ROLES.map(({ role, label }) => (
        <li key={role}>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              const id = ids[role] ?? "";
              router.push(
                role === "admin"
                  ? `/tools/wireframe/admin?unit=${id}`
                  : `/tools/wireframe/${role}/${id}`,
              );
            }}
          >
            <label>
              {label}{" "}
              <input
                type="number"
                required={role !== "admin"}
                value={ids[role] ?? ""}
                onChange={(event) =>
                  setIds({ ...ids, [role]: event.target.value })
                }
              />
            </label>{" "}
            <button type="submit">Open {role} page</button>
          </form>
        </li>
      ))}
    </ul>
  );
}
