import LocalTime from "@/components/common/local-time";
import type { IssueAssignment } from "@/types/maintenance/models";

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
      <h2 id="provider-heading" className="text-section">
        Tradesperson
      </h2>
      <div className="mt-2 rounded-xl border border-default p-4">
        <p className="font-medium">{provider.business_name}</p>
        <p className="text-sm text-fg-tertiary">
          {completed_at ? (
            <>
              Visit done <LocalTime iso={completed_at} />
            </>
          ) : scheduled_at ? (
            <>
              Booked for <LocalTime iso={scheduled_at} />
            </>
          ) : (
            "Booked, no time set yet"
          )}
        </p>
        <dl className="mt-3 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-[auto_1fr]">
          {contact.map(
            ([label, value]) =>
              value && (
                <div key={label} className="contents">
                  <dt className="text-fg-tertiary">{label}</dt>
                  <dd className="break-words whitespace-pre-line">{value}</dd>
                </div>
              ),
          )}
        </dl>
      </div>
    </section>
  );
}
