import type { UserBrief } from "@/types/access/models";

export type BanStatus = "ACTIVE" | "EXPIRED" | "LIFTED";
export type BanType = "EMAIL" | "EMAIL_DOMAIN" | "PHONE" | "ACCOUNT";

export type Ban = {
  id: number;
  ban_type: BanType;
  value: string | null;
  user: UserBrief | null;
  reason: string;
  status: BanStatus;
  created_at: string;
  created_by: UserBrief | null;
  expires_at: string | null;
  lifted_at: string | null;
  lifted_by: UserBrief | null;
  lift_reason: string | null;
};

export type TokenStatus = "ACTIVE" | "REVOKED" | "EXPIRED";

export type AccessToken = {
  id: number;
  user: UserBrief;
  device_name: string | null;
  user_agent: string | null;
  ip_address: string | null;
  verified_method: string;
  status: TokenStatus;
  mfa_verified: boolean;
  is_current: boolean;
  created_at: string;
  last_used_at: string;
  expires_at: string;
  revoked_at: string | null;
};

export type ListFilters = {
  q?: string;
  status?: string;
  type?: string;
  page?: number;
};
