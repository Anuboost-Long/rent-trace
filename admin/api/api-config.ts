export const BaseUrl = process.env.API_BASE_URL ?? "http://localhost:8000/api";

const byEndpoint = (path: string) => `${BaseUrl}/${path}`;

const propertyApi = (root: string) => ({
  list: byEndpoint(`${root}/`),
  detail: (id: number | string) => byEndpoint(`${root}/${id}/`),
  units: (id: number | string) => byEndpoint(`${root}/${id}/units/`),
  unit: (id: number | string, unitId: number) =>
    byEndpoint(`${root}/${id}/units/${unitId}/`),
});

const propertyFiles = (root: string) => {
  const files = (id: number | string, unitId?: number | string) =>
    `${root}/${id}${unitId ? `/units/${unitId}` : ""}/files/`;
  return {
    list: (id: number | string, unitId?: number | string) =>
      byEndpoint(files(id, unitId)),
    detail: (
      id: number | string,
      fileId: number | string,
      unitId?: number | string,
    ) => byEndpoint(`${files(id, unitId)}${fileId}/`),
    content: (
      id: number | string,
      fileId: number | string,
      unitId?: number | string,
    ) => byEndpoint(`${files(id, unitId)}${fileId}/content/`),
  };
};

export const EndPoints = {
  property_files: {
    admin: propertyFiles("properties"),
    landlord: propertyFiles("landlord/properties"),
  },
  bans: {
    list: byEndpoint("bans/"),
    lift: (id: number) => byEndpoint(`bans/${id}/lift/`),
  },
  tokens: {
    list: byEndpoint("tokens/"),
    revoke: (id: number) => byEndpoint(`tokens/${id}/revoke/`),
  },
  access: {
    permissions: byEndpoint("access/permissions/"),
    permission: (code: string) => byEndpoint(`access/permissions/${code}/`),
    holders: (code: string) =>
      byEndpoint(`access/permissions/${code}/holders/`),
    grant_list: byEndpoint("access/grants/"),
    members: (roleCode: string) =>
      byEndpoint(`access/roles/${roleCode}/members/`),
    member: (roleCode: string, userId: number) =>
      byEndpoint(`access/roles/${roleCode}/members/${userId}/`),
    roles: byEndpoint("access/roles/"),
    role: (code: string) => byEndpoint(`access/roles/${code}/`),
    user_permissions: (id: number | string) =>
      byEndpoint(`access/users/${id}/permissions/`),
    grants: (id: number | string) => byEndpoint(`access/users/${id}/grants/`),
    grant: (id: number | string, code: string) =>
      byEndpoint(`access/users/${id}/grants/${code}/`),
  },
  locations: {
    suburbs: byEndpoint("locations/suburbs/"),
  },
  properties: {
    ...propertyApi("properties"),
    owner_options: byEndpoint("properties/owner-options/"),
  },
  landlord_properties: propertyApi("landlord/properties"),
  users: {
    list: byEndpoint("users/"),
    all: byEndpoint("users/all/"),
    detail: (id: number | string) => byEndpoint(`users/${id}/`),
    activate: (id: number | string) => byEndpoint(`users/${id}/activate/`),
    deactivate: (id: number | string) => byEndpoint(`users/${id}/deactivate/`),
  },
  auth: {
    sign_up: byEndpoint("auth/sign-up/"),
    verify_email: byEndpoint("auth/verify-email/"),
    resend_verification: byEndpoint("auth/resend-verification/"),
    sign_in: byEndpoint("auth/sign-in/"),
    google: byEndpoint("auth/google/"),
    onboarding: byEndpoint("auth/onboarding/"),
    refresh: byEndpoint("auth/refresh/"),
    sign_out: byEndpoint("auth/sign-out/"),
    me: byEndpoint("auth/me/"),
    profile: byEndpoint("auth/profile/"),
    change_password: byEndpoint("auth/change-password/"),
    mfa_enrol: byEndpoint("auth/mfa/enrol/"),
    mfa_confirm: byEndpoint("auth/mfa/confirm/"),
    mfa_verify: byEndpoint("auth/mfa/verify/"),
  },
};
