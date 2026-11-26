"use client";
import Button from "@/components/common/button";
import ButtonLink from "@/components/common/button-link";
import { Route } from "@/constants/web-routes";
import useAcceptInvitation from "@/hooks/form/useAcceptInvitation";

export default function AcceptInvitation({
  token,
}: Readonly<{ token: string }>) {
  const { pending, error, accepted, accept } = useAcceptInvitation(token);

  if (accepted) {
    return (
      <div className="mt-4">
        <p>
          {accepted.joined
            ? `You've joined ${accepted.property_name}, ${accepted.unit_name}.`
            : `You said yes to joining ${accepted.property_name}, ${accepted.unit_name}. The landlord still has to approve it. We'll tell you when they do.`}
        </p>
        <ButtonLink href={Route.tenant.tenancies} className="mt-6">
          View your tenancies
        </ButtonLink>
      </div>
    );
  }

  return (
    <div className="mt-4">
      <p className="text-fg-secondary">
        Sign in with the email this invitation was sent to, then accept it to
        join the tenancy.
      </p>
      {error && (
        <p role="alert" className="mt-4 text-sm text-error">
          {error.message}
        </p>
      )}
      <Button className="mt-6" onClick={accept} pending={pending}>
        {pending ? "Joining…" : "Accept invitation"}
      </Button>
    </div>
  );
}
