import type { User } from "@/types/auth/models";

import { Route } from "./web-routes";

export type Audience = "tenant" | "landlord" | "admin";

const AUDIENCES: Audience[] = ["admin", "landlord", "tenant"];

type Member = Pick<User, "roles" | "is_admin">;

export const isMemberOf = (audience: Audience, member: Member) =>
  audience === "admin"
    ? member.is_admin
    : member.roles.includes(audience.toUpperCase());

export const audienceFor = (member: Member) =>
  AUDIENCES.find((audience) => isMemberOf(audience, member));

export const AUDIENCE_LABEL: Record<Audience, string> = {
  admin: "Admin",
  landlord: "Landlord",
  tenant: "Tenant",
};

export const homePathFor = (member: Member) => {
  const audience = audienceFor(member);
  return audience ? `/${audience}` : Route.auth.onboarding;
};
