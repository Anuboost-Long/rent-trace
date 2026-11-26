import { handleGetOverview } from "@/api/services/overview/serve-action";
import Card from "@/components/common/card";
import LocalTime from "@/components/common/local-time";
import { ActivityLabel } from "@/constants/overview";
import { TenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import type { TenancyAudience, TenancyStatus } from "@/types/tenancies/models";
import Link from "next/link";

const STATUS_SHADE: Record<TenancyStatus, string> = {
  ACTIVE: "bg-brand",
  PENDING: "bg-brand/60",
  DRAFT: "bg-brand/40",
  ENDED: "bg-brand/20",
  CANCELLED: "bg-muted",
};

const fullName = (person: { first_name: string; last_name: string }) =>
  `${person.first_name} ${person.last_name}`;

export default async function Dashboard({
  audience,
}: Readonly<{ audience: TenancyAudience }>) {
  const { data, error } = await handleGetOverview(audience);
  if (error) {
    return (
      <p role="alert" className="text-error">
        {error.message}
      </p>
    );
  }

  const { tenancies, people, properties, active_bans, activity } = data;
  const statuses = tenancies
    ? (Object.keys(STATUS_SHADE) as TenancyStatus[]).map((status) => ({
        status,
        count: tenancies.by_status[status],
      }))
    : [];
  const total = statuses.reduce((sum, part) => sum + part.count, 0);

  const isAdmin = audience === "admin";
  const tenanciesHref = isAdmin
    ? Route.admin.tenancies
    : Route.landlord.tenancies;

  const stats: (StatCardProp | null)[] = isAdmin
    ? [
        people && {
          value: people.suspended,
          label: "Suspended accounts",
          hint: `Out of ${people.users.toLocaleString("en-GB")} accounts`,
          href: `${Route.admin.users}?status=SUSPENDED`,
        },
        active_bans !== null
          ? {
              value: active_bans,
              label: "Active bans",
              hint: "Emails, domains and accounts",
              href: Route.admin.bans,
            }
          : null,
      ]
    : [
        properties && {
          value: properties.properties,
          label: "Properties",
          hint: `${properties.units.toLocaleString("en-GB")} units`,
          href: Route.landlord.properties,
        },
        tenancies && {
          value: tenancies.by_status.ACTIVE,
          label: "Active tenancies",
          hint: `${total} in all`,
          href: tenanciesHref,
        },
      ];
  if (tenancies) {
    stats.push(
      {
        value: tenancies.pending_invitations,
        label: "Invitations waiting",
        hint: `${tenancies.expired_invitations} expired unanswered`,
        href: tenanciesHref,
      },
      {
        value: tenancies.ending_soon,
        label: "Tenancies ending soon",
        hint: "Within the next 60 days",
        href: tenanciesHref,
      },
    );
  }
  const cards = stats.filter((card): card is StatCardProp => Boolean(card));

  return (
    <div className="flex flex-col gap-6">
      {cards.length > 0 && (
        <ul className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {cards.map((card) => (
            <li key={card.label}>
              <StatCard {...card} />
            </li>
          ))}
        </ul>
      )}

      {(tenancies || activity) && (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_24rem] lg:items-start">
          {tenancies && (
            <Card
              title="Tenancies"
              action={
                <Link
                  href={tenanciesHref}
                  className="text-body-sm font-semibold text-fg-brand hover:underline"
                >
                  See all
                </Link>
              }
            >
              <p className="text-display tabular-nums">
                {tenancies.by_status.ACTIVE}
                <span className="ml-2 text-body font-normal text-fg-secondary">
                  active of {total}
                </span>
              </p>
              {total > 0 && (
                <div
                  role="img"
                  aria-label="Tenancies by status"
                  className="mt-4 flex h-2 gap-0.5 overflow-hidden rounded-full"
                >
                  {statuses.map((part) => (
                    <div
                      key={part.status}
                      className={STATUS_SHADE[part.status]}
                      style={{ flexGrow: part.count }}
                    />
                  ))}
                </div>
              )}
              <ul className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-body-sm">
                {statuses.map((part) => (
                  <li key={part.status} className="flex items-center gap-2">
                    <span
                      aria-hidden
                      className={`size-2 rounded-full ${STATUS_SHADE[part.status]}`}
                    />
                    <span className="text-fg-secondary">
                      {TenancyStatusLabel[part.status]}
                    </span>
                    <span className="font-medium tabular-nums">
                      {part.count}
                    </span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {activity && (
            <Card title="Recent Admin actions">
              {activity.length === 0 ? (
                <p className="text-body-sm text-fg-secondary">
                  Nothing has changed yet.
                </p>
              ) : (
                <ol>
                  {activity.map((entry, index) => (
                    <li
                      key={`${entry.at}-${entry.action}-${entry.person.id}`}
                      className="relative pb-4 pl-6 last:pb-0"
                    >
                      {index < activity.length - 1 && (
                        <span
                          aria-hidden
                          className="absolute top-4 bottom-0 left-[4px] w-px bg-strong"
                        />
                      )}
                      <span
                        aria-hidden
                        className="absolute top-1.5 left-0 size-2.5 rounded-full bg-neutral-accent"
                      />
                      <p className="text-body-sm">
                        {entry.by ? fullName(entry.by) : "Someone"}{" "}
                        {ActivityLabel[entry.action] ?? "changed"}{" "}
                        <Link
                          href={Route.admin.user(entry.person.id)}
                          className="font-medium text-fg-brand hover:underline"
                        >
                          {fullName(entry.person)}
                        </Link>
                      </p>
                      <p className="text-caption font-normal text-fg-secondary">
                        <LocalTime iso={entry.at} withTime />
                      </p>
                    </li>
                  ))}
                </ol>
              )}
            </Card>
          )}
        </div>
      )}

      {cards.length === 0 && !tenancies && !activity && (
        <p className="text-fg-secondary">
          Your role doesn&apos;t show any figures here yet.
        </p>
      )}
    </div>
  );
}

type StatCardProp = Readonly<{
  value: number;
  label: string;
  hint: string;
  href: string;
}>;

function StatCard({ value, label, hint, href }: StatCardProp) {
  return (
    <Link
      href={href}
      className="block h-full rounded-xl border border-default bg-background p-5 transition-shadow hover:shadow-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-border motion-reduce:transition-none"
    >
      <p className="text-display tabular-nums">
        {value.toLocaleString("en-GB")}
      </p>
      <p className="mt-2 text-body">{label}</p>
      <p className="mt-1 text-caption font-normal text-fg-secondary">{hint}</p>
    </Link>
  );
}
