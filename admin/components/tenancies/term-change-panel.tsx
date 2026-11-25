"use client";
import Button from "@/components/common/button";
import Can from "@/components/common/can";
import LocalTime from "@/components/common/local-time";
import { TenancyAccess } from "@/constants/tenancies";
import useTermChange from "@/hooks/form/useTermChange";
import type { TenancyAudience, TermChange } from "@/types/tenancies/models";

import { Approvals, ChangedTerms } from "./term-change-summary";

type TermChangePanelProp = Readonly<{
  audience: TenancyAudience;
  tenancyId: number;
  change: TermChange;
}>;

export default function TermChangePanel({
  audience,
  tenancyId,
  change,
}: TermChangePanelProp) {
  const { pending, error, withdraw } = useTermChange(tenancyId);
  const expired = change.status === "EXPIRED";

  return (
    <section
      aria-labelledby="term-change-heading"
      className="mb-8 rounded-xl border border-default p-5"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="term-change-heading" className="text-section">
            {expired ? "Proposal expired" : "Waiting for tenants to approve"}
          </h2>
          <p className="mt-1 text-sm text-fg-secondary">
            {expired ? (
              "The tenants didn't answer in time. Edit the tenancy to send it again."
            ) : (
              <>
                This rise only takes effect once every tenant approves. It
                expires on <LocalTime iso={change.expires_at} />.
              </>
            )}
          </p>
        </div>
        <Can permission={TenancyAccess[audience].update}>
          <Button
            variant="quiet"
            size="sm"
            disabled={pending}
            onClick={() => withdraw(change.id, audience)}
          >
            Withdraw
          </Button>
        </Can>
      </div>
      <div className="mt-3">
        <ChangedTerms change={change} />
      </div>
      {!expired && (
        <div className="mt-3">
          <Approvals change={change} />
        </div>
      )}
      {error && (
        <p role="alert" className="mt-3 text-sm text-error">
          {error.message}
        </p>
      )}
    </section>
  );
}
