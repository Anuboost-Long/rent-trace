import {
  handleGetRoles,
  handleGetUserPermissions,
} from "@/api/services/access/serve-action";
import {
  handleGetUser,
  handleGetUsers,
} from "@/api/services/users/serve-action";
import type { UserPermissions } from "@/types/access/models";
import type { UserDetail } from "@/types/users/models";

export type TeamMember = { user: UserDetail; access: UserPermissions | null };

// Everyone holding an admin-kind role, with their details and permissions. The admin team is
// small, so this asks for each person's detail and permissions one by one.
export const getAdminTeam = async () => {
  const { data: roles, error } = await handleGetRoles();
  if (error) return { data: null, error };

  const adminRoles = roles.filter((role) => role.kind === "ADMIN");
  const pages = await Promise.all(
    adminRoles.map((role) =>
      handleGetUsers({ role: role.code, page_size: 100 }),
    ),
  );
  const failed = pages.find((page) => page.error);
  if (failed?.error) return { data: null, error: failed.error };

  const ids = [
    ...new Set(
      pages.flatMap((page) => page.data!.results.map((user) => user.id)),
    ),
  ];
  const members = await Promise.all(
    ids.map(async (id): Promise<TeamMember | null> => {
      const [user, access] = await Promise.all([
        handleGetUser(id),
        handleGetUserPermissions(id),
      ]);
      return user.data ? { user: user.data, access: access.data } : null;
    }),
  );

  const team = members
    .filter((member): member is TeamMember => member !== null)
    .sort((a, b) =>
      `${a.user.first_name} ${a.user.last_name}`.localeCompare(
        `${b.user.first_name} ${b.user.last_name}`,
      ),
    );
  return { data: team, error: null };
};
