export type UserSummary = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  roles: string[];
  role_names: string[];
  is_admin: boolean;
  account_status: "ACTIVE" | "SUSPENDED";
  is_top_level_admin: boolean;
  email_verified_at: string | null;
  last_login_at: string | null;
  created_at: string;
};

export type UserDetail = UserSummary & {
  phone_number: string | null;
  auth_method: string;
};

export type UserOption = Pick<
  UserSummary,
  "id" | "email" | "first_name" | "last_name" | "roles"
>;

export type UserPage = {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  results: UserSummary[];
};

export type UserFilters = {
  q?: string;
  role?: string;
  status?: string;
  page?: number;
  page_size?: number;
};

export type CreateUserBody = {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  roles: string[];
};

export type UpdateUserBody = Partial<{
  first_name: string;
  last_name: string;
  phone_number: string;
  roles: string[];
}>;
