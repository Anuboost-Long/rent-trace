"use client";
import { UserAtom } from "@/api/services/auth/jotai";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import TextInput from "@/components/common/inputs/text-input";
import ConfirmDialog from "@/components/common/modal/confirm-dialog";
import useHousemateRequests from "@/hooks/form/useHousemateRequests";
import type { Housemate, HousemateRequest } from "@/types/tenancies/models";
import { formatDate } from "@/utils/format-date";
import clsx from "clsx";
import { useAtomValue } from "jotai";
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
const rowClassName = "flex items-start gap-4 py-4";

const initialOf = (text: string) => text.trim().charAt(0).toUpperCase();

type MarkProp = Readonly<{ letter: string; joined: boolean }>;

function Mark({ letter, joined }: MarkProp) {
  return (
    <span
      aria-hidden
      className={clsx(
        "grid size-10 shrink-0 place-items-center rounded-full text-sm font-medium",
        joined
          ? "bg-foreground/10"
          : "border border-dashed border-foreground/30 text-foreground/60",
      )}
    >
      {letter}
    </span>
  );
}

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
  const me = useAtomValue(UserAtom);
  const { pending, error, request, withdraw } = useHousemateRequests(tenancyId);
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [sentTo, setSentTo] = useState<string | null>(null);

  const myName = me ? `${me.first_name} ${me.last_name}`.trim() : "You";
  const peopleCount = housemates.length + 1;
  const isFull = maxPeople !== null && peopleCount >= maxPeople;
  const livesAlone = housemates.length === 0 && requests.length === 0;

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
    <section aria-labelledby="people-heading" className="mt-12">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-3">
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

      <ul className="mt-2 divide-y divide-foreground/10">
        <li className={rowClassName}>
          <Mark letter={initialOf(myName)} joined />
          <div className="flex min-w-0 flex-1 items-center justify-between gap-3 self-center">
            <p className="truncate font-medium">
              {myName}
              {me && (
                <span className="font-normal text-foreground/60"> (you)</span>
              )}
            </p>
            {youArePrimary && <p className={mutedText}>Primary tenant</p>}
          </div>
        </li>
        {housemates.map((mate) => (
          <li
            key={`${mate.first_name}-${mate.last_name}`}
            className={rowClassName}
          >
            <Mark letter={initialOf(mate.first_name)} joined />
            <div className="flex min-w-0 flex-1 items-center justify-between gap-3 self-center">
              <p className="truncate font-medium">
                {mate.first_name} {mate.last_name}
              </p>
              {mate.is_primary && <p className={mutedText}>Primary tenant</p>}
            </div>
          </li>
        ))}
      </ul>

      {livesAlone && (
        <p className="mt-4 max-w-[65ch] text-sm text-foreground/70">
          Living with someone else? Invite them here. Your landlord and the
          person you invite both approve before they join.
        </p>
      )}

      {requests.length > 0 && (
        <>
          <h3 className="mt-10 text-sm font-medium text-foreground/70">
            Invites
          </h3>
          <ul className="mt-1 divide-y divide-foreground/10">
            {requests.map((item) => {
              const isOpen = item.status === "PENDING";
              return (
                <li key={item.id} className={rowClassName}>
                  <Mark letter={initialOf(item.email)} joined={false} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-3">
                      <p className="min-w-0 truncate font-medium">
                        {item.email}
                      </p>
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
                      <p className="mt-1.5 flex flex-wrap items-center gap-x-5 gap-y-1 text-sm">
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
                  </div>
                </li>
              );
            })}
          </ul>
        </>
      )}

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
