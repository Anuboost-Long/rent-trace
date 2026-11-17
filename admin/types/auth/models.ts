export type Role = "TENANT" | "LANDLORD";

export type MfaStatus = "NOT_REQUIRED" | "ENROL" | "VERIFY" | "VERIFIED";

export type User = {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string | null;
  auth_method: string;
  email_verified_at: string | null;
  roles: string[];
  role_names: string[];
  is_admin: boolean;
  is_top_level_admin: boolean;
  created_at: string;
  last_login_at: string | null;
};

export type Me = User & { mfa_status: MfaStatus; permissions: string[] };

export type MfaEnrolment = { secret: string; provisioning_uri: string };

export type MfaBackupCodes = { backup_codes: string[] };

export type SignedIn = {
  token_type: string;
  access_token: string;
  expires_in: number;
  refresh_token: string;
  needs_onboarding: boolean;
  mfa_status: MfaStatus;
  user: User;
};

export type SignInBody = { email: string; password: string };

export type SignUpBody = SignInBody & {
  first_name: string;
  last_name: string;
  role: Role;
};

export type OnboardingBody = {
  first_name: string;
  last_name: string;
  role: Role;
};

export type ProfileBody = {
  first_name: string;
  last_name: string;
  phone_number: string;
};

export type ChangePasswordBody = {
  current_password: string;
  new_password: string;
  sign_out_other_devices: boolean;
};

export type ResetPasswordBody = {
  token: string;
  new_password: string;
  sign_out_other_devices: boolean;
  code?: string;
};

export type ResetPreview = { requires_code: boolean };

export type Message = { detail: string };
