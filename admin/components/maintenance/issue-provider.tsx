import type { IssueAssignment } from "@/types/maintenance/models";
import { formatDate } from "@/utils/format-date";

type IssueProviderProp = Readonly<{ assignment: IssueAssignment }>;

export default function IssueProvider({ assignment }: IssueProviderProp) {
  const { provider, scheduled_at, completed_at } = assignment;
  const contact = [
    ["Contact", provider.contact_name],
    ["Phone", provider.phone_number],
    ["Email", provider.email],
    ["Website", provider.website],
    ["Address", provider.address],
  ];

  return (
    <section aria-labelledby="provider-heading" className="mb-8">
      <h2 id="provider-heading" className="text-lg font-semibold">
        Tradesperson
      </h2>
      <div className="mt-2 rounded-xl border border-foreground/15 p-4">
        <p className="font-medium">{provider.business_name}</p>
        <p className="text-sm text-foreground/60">
          {completed_at
            ? `Visit done ${formatDate(completed_at)}`
            : scheduled_at
              ? `Booked for ${formatDate(scheduled_at)}`
              : "Booked, no time set yet"}
        </p>
        <dl className="mt-3 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-[auto_1fr]">
          {contact.map(
            ([label, value]) =>
              value && (
                <div key={label} className="contents">
                  <dt className="text-foreground/60">{label}</dt>
                  <dd className="break-words whitespace-pre-line">{value}</dd>
                </div>
              ),
          )}
        </dl>
      </div>
    </section>
  );
}
