"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import TextInput from "@/components/common/inputs/text-input";
import useHousemateRequests from "@/hooks/form/useHousemateRequests";
import type { HousemateRequest } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import clsx from "clsx";
import { Check, Clock } from "lucide-react";
import { useRef } from "react";

type HousemateRequestsProp = Readonly<{
  tenancyId: number;
  requests: HousemateRequest[];
  canAsk: boolean;
  peopleCount: number;
  maxPeople: number | null;
}>;

const ENDED_LABEL: Record<string, string> = {
  ACCEPTED: "Joined",
  DECLINED: "Declined by your landlord",
  REVOKED: "Withdrawn",
  EXPIRED: "Expired",
};

type StepProp = Readonly<{
  done: boolean;
  doneText: string;
  waitingText: string;
}>;

function Step({ done, doneText, waitingText }: StepProp) {
  const Icon = done ? Check : Clock;
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5",
        done ? "text-foreground" : "text-foreground/60",
      )}
    >
      <Icon aria-hidden className="size-4 shrink-0" />
      {done ? doneText : waitingText}
    </span>
  );
}

export default function HousemateRequests({
  tenancyId,
  requests,
  canAsk,
  peopleCount,
  maxPeople,
}: HousemateRequestsProp) {
  const { pending, error, request, withdraw } = useHousemateRequests(tenancyId);
  const formRef = useRef<HTMLFormElement>(null);
  const isFull = maxPeople !== null && peopleCount >= maxPeople;

  return (
    <section aria-labelledby="housemate-heading" className="mt-10">
      <div className="flex items-baseline justify-between gap-4">
        <h2 id="housemate-heading" className="text-lg font-semibold">
          Add a housemate
        </h2>
        {maxPeople !== null && (
          <p className="text-sm text-foreground/60 tabular-nums">
            {peopleCount} of {maxPeople} people
          </p>
        )}
      </div>
      <p className="mt-1 text-sm text-foreground/70">
        Your landlord and the person you invite both have to agree before they
        join.
      </p>

      <Can permission="tenancies.invite_housemate">
        {canAsk &&
          (isFull ? (
            <p className="mt-5 text-sm text-foreground/70">
              This place is full, so you can&apos;t invite anyone right now.
            </p>
          ) : (
            <form
              ref={formRef}
              onSubmit={async (event) => {
                event.preventDefault();
                const email = new FormData(event.currentTarget).get("email");
                if (typeof email !== "string") return;
                if (await request(email)) formRef.current?.reset();
              }}
              className="mt-5 grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end"
            >
              <TextInput
                label="Email address"
                name="email"
                type="email"
                autoComplete="off"
                required
                error={error?.fields.email}
              />
              <Button type="submit" pending={pending}>
                Send invite
              </Button>
            </form>
          ))}
        {error && !error.fields.email && (
          <p role="alert" className="mt-3 text-sm text-red-600">
            {error.message}
          </p>
        )}
      </Can>

      {requests.length > 0 && (
        <ul className="mt-6 divide-y divide-foreground/15 overflow-hidden rounded-xl border border-foreground/15">
          {requests.map((item) => {
            const isOpen = item.status === "PENDING";
            return (
              <li key={item.id} className="p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="min-w-0 truncate font-medium">{item.email}</p>
                  {isOpen ? (
                    <Button
                      variant="quiet"
                      size="sm"
                      disabled={pending}
                      onClick={() => withdraw(item.id)}
                    >
                      Withdraw
                    </Button>
                  ) : (
                    <p className="shrink-0 text-sm text-foreground/60">
                      {ENDED_LABEL[item.status]}
                    </p>
                  )}
                </div>
                {isOpen && (
                  <p className="mt-2 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
                    <Step
                      done={!item.waiting_on.includes("LANDLORD")}
                      doneText="Landlord approved"
                      waitingText="Waiting for your landlord"
                    />
                    <Step
                      done={!item.waiting_on.includes("INVITEE")}
                      doneText="They accepted"
                      waitingText="Waiting for them"
                    />
                    <span className="text-foreground/60">
                      Expires {formatDate(item.expires_at)}
                    </span>
                  </p>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
