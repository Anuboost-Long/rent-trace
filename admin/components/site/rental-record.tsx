const RECORD: [string, string][] = [
  [
    "Rent and bond",
    "Set when the tenancy starts. An increase only takes effect once every tenant has approved it.",
  ],
  [
    "Condition notes",
    "Landlords write down the condition of a place and choose which tenants see each note.",
  ],
  [
    "Maintenance",
    "Tenants report what needs fixing. Both sides see where it stands, and an issue closes only when each side agrees.",
  ],
  [
    "Housemates",
    "Tenants invite the people they live with, and the landlord approves them before they join.",
  ],
];

export default function RentalRecord() {
  return (
    <section
      aria-labelledby="record-heading"
      className="mx-auto mt-24 grid w-full max-w-7xl gap-10 px-4 sm:px-6 lg:grid-cols-12 lg:gap-16"
    >
      <div className="lg:sticky lg:top-24 lg:col-span-5 lg:self-start">
        <h2
          id="record-heading"
          className="text-3xl font-semibold tracking-tight text-balance sm:text-4xl"
        >
          A record both sides can see
        </h2>
        <p className="mt-4 max-w-[44ch] text-lg text-fg-secondary">
          RentTrace keeps what happens in a tenancy in one place, so nobody has
          to rely on memory.
        </p>
      </div>
      <dl className="border-t border-default lg:col-span-7">
        {RECORD.map(([title, detail]) => (
          <div
            key={title}
            className="grid gap-2 border-b border-default py-7 sm:grid-cols-3 sm:gap-8"
          >
            <dt className="text-lg font-semibold">{title}</dt>
            <dd className="text-fg-secondary sm:col-span-2">{detail}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
