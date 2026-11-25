import LocalTime from "@/components/common/local-time";
import type { TenantCondition } from "@/types/conditions/models";

export default function TenantConditions({
  notes,
}: Readonly<{ notes: TenantCondition[] }>) {
  if (notes.length === 0) return null;

  return (
    <section aria-labelledby="unit-condition-heading" className="mt-12">
      <h2 id="unit-condition-heading" className="text-lg font-semibold">
        Condition of the unit
      </h2>
      <p className="mt-1 text-sm text-fg-tertiary">
        Notes your landlord chose to share.
      </p>
      <ul className="mt-2 divide-y divide-default">
        {notes.map((note) => (
          <li key={note.id} className="max-w-[65ch] py-4">
            <p className="font-medium">{note.title}</p>
            {note.description && (
              <p className="mt-1 whitespace-pre-line text-fg-secondary">
                {note.description}
              </p>
            )}
            <p className="mt-1.5 text-sm text-fg-tertiary">
              Checked <LocalTime iso={note.observed_at} />
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
