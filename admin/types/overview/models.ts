import type { UserBrief } from "@/types/access/models";
import type { TenancyStatus } from "@/types/tenancies/models";

export type ActivityEntry = {
  action: string;
  person: UserBrief;
  by: UserBrief | null;
  at: string;
};

export type Overview = {
  people: { users: number; suspended: number } | null;
  properties: { properties: number; units: number } | null;
  tenancies: {
    by_status: Record<TenancyStatus, number>;
    ending_soon: number;
    pending_invitations: number;
    expired_invitations: number;
  } | null;
  active_bans: number | null;
  activity: ActivityEntry[] | null;
};
