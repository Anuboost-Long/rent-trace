export const BanTypeLabel: Record<string, string> = {
  EMAIL: "Email",
  EMAIL_DOMAIN: "Email domain",
  PHONE: "Phone",
  ACCOUNT: "Account",
};

export const BanStatusLabel: Record<string, string> = {
  ACTIVE: "Active",
  EXPIRED: "Expired",
  LIFTED: "Lifted",
};

export const TokenStatusLabel: Record<string, string> = {
  ACTIVE: "Active",
  REVOKED: "Revoked",
  EXPIRED: "Expired",
};

export const CreatableBanTypeLabel: Record<string, string> = {
  EMAIL: "Email",
  EMAIL_DOMAIN: "Email domain",
  ACCOUNT: "Account",
};

export const BanDurationDays: Record<string, number | null> = {
  never: null,
  "1": 1,
  "7": 7,
  "30": 30,
  "90": 90,
};

export const BanDurationLabel: Record<string, string> = {
  never: "Never expires",
  "1": "1 day",
  "7": "7 days",
  "30": "30 days",
  "90": "90 days",
};

// Added to the sign-in URL as `reason` when a signed-in session could not be refreshed.
export const SESSION_ENDED = "session_ended";
