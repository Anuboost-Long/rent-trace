export const ContactRequestStatusLabel: Record<string, string> = {
  PENDING: "Waiting",
  ACCEPTED: "Accepted",
  DECLINED: "Declined",
  CANCELLED: "Cancelled",
  REVOKED: "Revoked",
};

export const OPEN_REQUEST_STATUSES = ["PENDING", "ACCEPTED"];

export type RequestAction = "cancel" | "accept" | "decline" | "revoke";

export const RequestActionCopy: Record<
  RequestAction,
  { button: string; title: string; message: string }
> = {
  cancel: {
    button: "Cancel request",
    title: "Cancel this request?",
    message:
      "The landlord won't see it any more. You can send a new one later.",
  },
  accept: {
    button: "Accept",
    title: "Accept this request?",
    message:
      "The tenant will see your name, email and phone number. You can revoke this later.",
  },
  decline: {
    button: "Decline",
    title: "Decline this request?",
    message: "The tenant is told you declined. Your details stay private.",
  },
  revoke: {
    button: "Revoke",
    title: "Revoke contact details?",
    message: "The tenant can no longer see your name, email and phone number.",
  },
};
