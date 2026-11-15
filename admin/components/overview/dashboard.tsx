import { handleGetOverview } from "@/api/services/overview/serve-action";
import LocalTime from "@/components/common/local-time";
import { ActivityLabel } from "@/constants/overview";
import { TenancyStatusLabel } from "@/constants/tenancies";
import { Route } from "@/constants/web-routes";
import type { TenancyAudience, TenancyStatus } from "@/types/tenancies/models";
import Link from "next/link";

const STATUS_SHADE: Record<TenancyStatus, string> = {
  ACTIVE: "bg-foreground",
  PENDING: "bg-foreground/60",
  DRAFT: "bg-foreground/40",
  ENDED: "bg-foreground/20",
  CANCELLED: "bg-foreground/10",
};

const fullName = (person: { first_name: string; last_name: string }) =>
  `${person.first_name} ${person.last_name}`;

export default async function Dashboard({
  audience,
}: Readonly<{ audience: TenancyAudience }>) {
  const { data, error } = await handleGetOverview(audience);
  if (error) {
    return (
      <p role="alert" className="text-red-600">
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

  const attention = tenancies
    ? [
        {
          label: "Tenancies ending within 60 days",
          count: tenancies.ending_soon,
        },
        {
          label: "Invitations waiting for an answer",
          count: tenancies.pending_invitations,
        },
        {
          label: "Invitations that expired unanswered",
          count: tenancies.expired_invitations,
        },
      ]
    : [];

  const figures = [
    people && { label: "Users", value: people.users },
    people && { label: "Suspended", value: people.suspended },
    properties && { label: "Properties", value: properties.properties },
    properties && { label: "Units", value: properties.units },
    active_bans !== null && { label: "Active bans", value: active_bans },
  ].filter((figure) => figure !== null && figure !== false);

  return (
    <div className="space-y-10">
      {tenancies && (
        <div className="grid gap-10 lg:grid-cols-3 lg:gap-12">
          <section
            aria-labelledby="tenancies-heading"
            className="lg:col-span-2"
          >
            <h2 id="tenancies-heading" className="text-sm text-foreground/70">
              Active tenancies
            </h2>
            <p className="mt-2 text-6xl font-semibold tabular-nums tracking-tight">
              {tenancies.by_status.ACTIVE}
            </p>
            <p className="mt-2 text-sm text-foreground/70">
              {total} {total === 1 ? "tenancy" : "tenancies"} in all.{" "}
              <Link
                href={
                  audience === "landlord"
                    ? Route.landlord.tenancies
                    : Route.admin.tenancies
                }
                className="underline"
              >
                See all
              </Link>
            </p>
            {total > 0 && (
              <div
                role="img"
                aria-label="Tenancies by status"
                className="mt-6 flex h-2 gap-0.5 overflow-hidden rounded-full"
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
            <ul className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-sm">
              {statuses.map((part) => (
                <li key={part.status} className="flex items-center gap-2">
                  <span
                    aria-hidden
                    className={`size-2 rounded-full ${STATUS_SHADE[part.status]}`}
                  />
                  <span className="text-foreground/70">
                    {TenancyStatusLabel[part.status]}
                  </span>
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
              {attention.map((item) => (
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
      )}

      {figures.length > 0 && (
        <dl className="grid grid-cols-2 gap-y-4 border-t border-foreground/15 pt-6 sm:grid-cols-5">
          {figures.map((figure) => (
            <div key={figure.label}>
              <dt className="text-xs text-foreground/70">{figure.label}</dt>
              <dd className="mt-1 text-lg font-medium tabular-nums">
                {figure.value.toLocaleString("en-GB")}
              </dd>
            </div>
          ))}
        </dl>
      )}

      {activity && (
        <section aria-labelledby="activity-heading">
          <h2 id="activity-heading" className="text-sm text-foreground/70">
            Recent activity
          </h2>
          {activity.length === 0 ? (
            <p className="mt-2 text-sm text-foreground/70">
              Nothing has changed yet.
            </p>
          ) : (
            <ul className="mt-2 divide-y divide-foreground/15 border-y border-foreground/15">
              {activity.map((entry) => (
                <li
                  key={`${entry.at}-${entry.action}-${entry.person.id}`}
                  className="flex justify-between gap-4 py-2.5 text-sm"
                >
                  <span>
                    {entry.by ? fullName(entry.by) : "Someone"}{" "}
                    {ActivityLabel[entry.action] ?? "changed"}{" "}
                    <Link
                      href={Route.admin.user(entry.person.id)}
                      className="underline-offset-2 hover:underline"
                    >
                      {fullName(entry.person)}
                    </Link>
                  </span>
                  <span className="shrink-0 text-foreground/70">
                    <LocalTime iso={entry.at} withTime />
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {!tenancies && figures.length === 0 && !activity && (
        <p className="text-foreground/70">
          Your role doesn&apos;t show any figures here yet.
        </p>
      )}
    </div>
  );
}
