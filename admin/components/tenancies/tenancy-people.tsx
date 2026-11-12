"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useHousemateRequests from "@/hooks/form/useHousemateRequests";
import type { Housemate, HousemateRequest } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import clsx from "clsx";
import { Check, Clock, UserPlus } from "lucide-react";
import { useState } from "react";

type TenancyPeopleProp = Readonly<{
  tenancyId: number;
  youArePrimary: boolean;
  housemates: Housemate[];
  requests: HousemateRequest[];
  canInvite: boolean;
  maxPeople: number | null;
}>;

const ENDED_LABEL: Record<string, string> = {
  ACCEPTED: "Joined",
  DECLINED: "Declined by your landlord",
  REVOKED: "Withdrawn",
  EXPIRED: "Expired",
};

const mutedText = "text-sm text-foreground/60";

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

export default function TenancyPeople({
  tenancyId,
  youArePrimary,
  housemates,
  requests,
  canInvite,
  maxPeople,
}: TenancyPeopleProp) {
  const { pending, error, request, withdraw } = useHousemateRequests(tenancyId);
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [sentTo, setSentTo] = useState<string | null>(null);

  const peopleCount = housemates.length + 1;
  const isFull = maxPeople !== null && peopleCount >= maxPeople;

  const close = () => {
    setOpen(false);
    setEmail("");
  };

  const send = async () => {
    const address = email.trim();
    if (await request(address)) {
      setSentTo(address);
      close();
    }
  };

  return (
    <section aria-labelledby="people-heading" className="mt-10">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2">
        <div className="flex items-baseline gap-3">
          <h2 id="people-heading" className="text-lg font-semibold">
            People
          </h2>
          <p className={clsx(mutedText, "tabular-nums")}>
            {maxPeople === null
              ? peopleCount
              : `${peopleCount} of ${maxPeople}`}
          </p>
        </div>
        <Can permission="tenancies.invite_housemate">
          {canInvite && (
            <Button
              variant="quiet"
              size="sm"
              className="gap-2"
              disabled={isFull}
              title={isFull ? "This place is full" : undefined}
              onClick={() => setOpen(true)}
            >
              <UserPlus aria-hidden className="size-4" />
              Invite housemate
            </Button>
          )}
        </Can>
      </div>

      {sentTo && (
        <output className="mt-3 block text-sm">
          Invite sent to {sentTo}. We&apos;ve told your landlord too.
        </output>
      )}

      <ul className="mt-4 divide-y divide-foreground/15 overflow-hidden rounded-xl border border-foreground/15">
        <li className="flex items-center justify-between gap-3 p-4">
          <span className="font-medium">You</span>
          {youArePrimary && <span className={mutedText}>Primary tenant</span>}
        </li>
        {housemates.map((mate) => (
          <li
            key={`${mate.first_name}-${mate.last_name}`}
            className="flex items-center justify-between gap-3 p-4"
          >
            <span className="font-medium">
              {mate.first_name} {mate.last_name}
            </span>
            {mate.is_primary && (
              <span className={mutedText}>Primary tenant</span>
            )}
          </li>
        ))}
        {requests.length > 0 && (
          <li
            aria-hidden
            className="bg-foreground/5 px-4 py-2 text-xs font-medium text-foreground/60"
          >
            Invites
          </li>
        )}
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
                  <p className={clsx(mutedText, "shrink-0")}>
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

      {open && (
        <ConfirmDialog
          open
          title="Invite a housemate"
          message="We email them and your landlord. They only join once your landlord approves and they accept."
          confirmLabel="Send invite"
          pending={pending}
          confirmDisabled={email.trim() === ""}
          error={error?.fields.email ?? error?.message}
          onConfirm={send}
          onCancel={close}
        >
          <form
            onSubmit={(event) => {
              event.preventDefault();
              if (email.trim() !== "") void send();
            }}
          >
            <TextInput
              label="Their email"
              name="email"
              type="email"
              autoComplete="off"
              placeholder="name@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </form>
        </ConfirmDialog>
      )}
    </section>
  );
}
