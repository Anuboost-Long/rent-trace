import { handleGetMyInvitations } from "@/api/services/tenancies/serve-action";
import LocalTime from "@/components/common/local-time";

import AcceptInvitationButton from "./accept-invitation-button";

export default async function MyInvitations() {
  const { data } = await handleGetMyInvitations();
  if (!data || data.length === 0) return null;

  return (
    <section aria-labelledby="invitations-heading" className="mb-10">
      <h2 id="invitations-heading" className="text-section">
        Invitations waiting for you
      </h2>
      <ul className="mt-3 divide-y divide-default rounded-xl border border-default">
        {data.map((invitation) => (
          <li
            key={invitation.id}
            className="flex flex-wrap items-center justify-between gap-4 p-4"
          >
            <div>
              <p className="font-medium">
                {invitation.property_name}, {invitation.unit_name}
              </p>
              <p className="text-sm text-fg-secondary">
                {invitation.invited_by
                  ? `${invitation.invited_by} invited you`
                  : "You've been invited"}
                {invitation.is_primary && " as the primary tenant"}. Expires{" "}
                <LocalTime iso={invitation.expires_at} />.
                {invitation.requested_by_tenant &&
                  invitation.waiting_on.includes("LANDLORD") &&
                  " The landlord also has to approve before you join."}
              </p>
              {!invitation.waiting_on.includes("INVITEE") && (
                <p className="mt-1 text-sm font-medium">
                  You accepted. Waiting for the landlord to approve.
                </p>
              )}
            </div>
            {invitation.waiting_on.includes("INVITEE") && (
              <AcceptInvitationButton invitationId={invitation.id} />
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
