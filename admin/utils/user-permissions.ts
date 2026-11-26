import type { Me } from "@/types/auth/models";
import type { UserSummary } from "@/types/users/models";

type Actor = Pick<Me, "id" | "is_top_level_admin" | "permissions">;
type Target = Pick<UserSummary, "id" | "is_top_level_admin">;

export const canEditUser = (actor: Actor) =>
  actor.permissions.includes("accounts.update");

export const canToggleUser = (actor: Actor, target: Target) =>
  actor.permissions.includes("accounts.manage") &&
  actor.id !== target.id &&
  !target.is_top_level_admin;

export const canDeleteUser = (actor: Actor, target: Target) =>
  actor.permissions.includes("accounts.delete") &&
  actor.id !== target.id &&
  !target.is_top_level_admin;

export const canBanUser = (actor: Actor, target: Target) =>
  actor.permissions.includes("bans.manage") &&
  actor.id !== target.id &&
  !target.is_top_level_admin;
