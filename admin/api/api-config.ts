export const BaseUrl = process.env.API_BASE_URL ?? "http://localhost:8000/api";

const byEndpoint = (path: string) => `${BaseUrl}/${path}`;

const propertyApi = (root: string) => ({
  list: byEndpoint(`${root}/`),
  detail: (id: number | string) => byEndpoint(`${root}/${id}/`),
  units: (id: number | string) => byEndpoint(`${root}/${id}/units/`),
  unit: (id: number | string, unitId: number) =>
    byEndpoint(`${root}/${id}/units/${unitId}/`),
});

const tenancyApi = (root: string) => ({
  list: byEndpoint(`${root}/`),
  detail: (id: number | string) => byEndpoint(`${root}/${id}/`),
  invitations: (id: number | string) =>
    byEndpoint(`${root}/${id}/invitations/`),
  invitation_action: (id: number, invitationId: number, action: string) =>
    byEndpoint(`${root}/${id}/invitations/${invitationId}/${action}/`),
});

const propertyFiles = (root: string) => {
  const files = (id: number | string, unitId?: number | string) => {
    const unitPath = unitId ? "/units/" + unitId : "";
    return `${root}/${id}${unitPath}/files/`;
  };
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
  listings: {
    list: byEndpoint("public/listings/"),
    places: byEndpoint("public/listings/places/"),
    detail: (id: number | string) => byEndpoint(`public/listings/${id}/`),
    photo: (id: number | string, fileId: number | string) =>
      byEndpoint(`public/listings/${id}/photos/${fileId}/`),
  },
  property_files: {
    admin: propertyFiles("properties"),
    landlord: propertyFiles("landlord/properties"),
  },
  contact_requests: {
    tenant: {
      list: byEndpoint("tenant/contact-requests/"),
      cancel: (id: number) =>
        byEndpoint(`tenant/contact-requests/${id}/cancel/`),
    },
    landlord: {
      list: byEndpoint("landlord/contact-requests/"),
      respond: (id: number, action: string) =>
        byEndpoint(`landlord/contact-requests/${id}/${action}/`),
    },
  },
  overview: byEndpoint("overview/"),
  notifications: {
    list: byEndpoint("notifications/"),
    unread_count: byEndpoint("notifications/unread-count/"),
    read_all: byEndpoint("notifications/read-all/"),
    read: (id: number) => byEndpoint(`notifications/${id}/read/`),
  },
  tenancies: tenancyApi("tenancies"),
  landlord_tenancies: tenancyApi("landlord/tenancies"),
  tenant_invitations: {
    list: byEndpoint("tenant/invitations/"),
    accept_by_id: (id: number) =>
      byEndpoint(`tenant/invitations/${id}/accept/`),
    accept: byEndpoint("tenant/invitations/accept/"),
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
