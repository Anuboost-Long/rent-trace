const tenancyBreakdown = [
  { label: "Current", count: 658, shade: "bg-foreground" },
  { label: "Ending within 60 days", count: 61, shade: "bg-foreground/50" },
  { label: "Rent overdue", count: 23, shade: "bg-foreground/20" },
];

const needsAttention = [
  { label: "Maintenance open over 7 days", count: 9 },
  { label: "Landlord accounts awaiting verification", count: 14 },
  { label: "Disputed rent records", count: 4 },
];

const platformFigures = [
  { label: "Users", value: "1,284" },
  { label: "Properties", value: "903" },
  { label: "Open maintenance", value: "58" },
  { label: "Active bans", value: "17" },
];

const activity = [
  { text: "Landlord account created", when: "12 min ago" },
  { text: "Grant revoked: bans.view", when: "1 hour ago" },
  { text: "Email domain banned", when: "Yesterday" },
];

const total = tenancyBreakdown.reduce((sum, part) => sum + part.count, 0);

export default function MockDashboard() {
  return (
    <div className="space-y-10">
      <div className="grid gap-10 lg:grid-cols-3 lg:gap-12">
        <section aria-labelledby="tenancies-heading" className="lg:col-span-2">
          <h2 id="tenancies-heading" className="text-sm text-foreground/70">
            Active tenancies
          </h2>
          <p className="mt-2 text-6xl font-semibold tabular-nums tracking-tight">
            {total}
          </p>
          <p className="mt-2 text-sm text-foreground/70">
            12 more than last month · sample data
          </p>
          <div
            role="img"
            aria-label="Tenancies by status"
            className="mt-6 flex h-2 gap-0.5 overflow-hidden rounded-full"
          >
            {tenancyBreakdown.map((part) => (
              <div
                key={part.label}
                className={part.shade}
                style={{ flexGrow: part.count }}
              />
            ))}
          </div>
          <ul className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-sm">
            {tenancyBreakdown.map((part) => (
              <li key={part.label} className="flex items-center gap-2">
                <span
                  aria-hidden
                  className={`size-2 rounded-full ${part.shade}`}
                />
                <span className="text-foreground/70">{part.label}</span>
                <span className="font-medium tabular-nums">{part.count}</span>
              </li>
            ))}
          </ul>
        </section>

        <section aria-labelledby="attention-heading">
          <h2 id="attention-heading" className="text-sm text-foreground/70">
            Needs attention
          </h2>
          <ul className="mt-2 divide-y divide-foreground/15">
            {needsAttention.map((item) => (
              <li
                key={item.label}
                className="flex items-baseline justify-between gap-4 py-3"
              >
                <span className="text-sm">{item.label}</span>
                <span className="text-lg font-semibold tabular-nums">
                  {item.count}
                </span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <dl className="grid grid-cols-2 gap-y-4 border-t border-foreground/15 pt-6 sm:grid-cols-4">
        {platformFigures.map((figure) => (
          <div key={figure.label}>
            <dt className="text-xs text-foreground/70">{figure.label}</dt>
            <dd className="mt-1 text-lg font-medium tabular-nums">
              {figure.value}
            </dd>
          </div>
        ))}
      </dl>

      <section aria-labelledby="activity-heading">
        <h2 id="activity-heading" className="text-sm text-foreground/70">
          Recent activity
        </h2>
        <ul className="mt-2 divide-y divide-foreground/15 border-y border-foreground/15">
          {activity.map((entry) => (
            <li
              key={entry.text}
              className="flex justify-between gap-4 py-2.5 text-sm"
            >
              <span>{entry.text}</span>
              <span className="shrink-0 text-foreground/70">{entry.when}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
