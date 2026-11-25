export const BaseUrl = process.env.API_BASE_URL ?? "http://localhost:8000/api";

const byEndpoint = (path: string) => `${BaseUrl}/${path}`;

const propertyApi = (root: string) => ({
  list: byEndpoint(`${root}/`),
  detail: (id: number | string) => byEndpoint(`${root}/${id}/`),
  units: (id: number | string) => byEndpoint(`${root}/${id}/units/`),
  unit: (id: number | string, unitId: number) =>
    byEndpoint(`${root}/${id}/units/${unitId}/`),
  unit_occupancy: (id: number | string, unitId: number) =>
    byEndpoint(`${root}/${id}/units/${unitId}/occupancy/`),
});

const tenancyApi = (root: string) => ({
  list: byEndpoint(`${root}/`),
  detail: (id: number | string) => byEndpoint(`${root}/${id}/`),
  invitations: (id: number | string) =>
    byEndpoint(`${root}/${id}/invitations/`),
  invitation_action: (id: number, invitationId: number, action: string) =>
    byEndpoint(`${root}/${id}/invitations/${invitationId}/${action}/`),
  action: (id: number, action: string) =>
    byEndpoint(`${root}/${id}/${action}/`),
  withdraw_terms: (id: number, changeId: number) =>
    byEndpoint(`${root}/${id}/changes/${changeId}/withdraw/`),
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
    admin: { list: byEndpoint("admin/contact-requests/") },
    landlord: {
      list: byEndpoint("landlord/contact-requests/"),
      respond: (id: number, action: string) =>
        byEndpoint(`landlord/contact-requests/${id}/${action}/`),
    },
  },
  overview: byEndpoint("overview/"),
  landlord_overview: byEndpoint("landlord/overview/"),
  admin_providers: {
    list: byEndpoint("admin/providers/"),
    categories: byEndpoint("admin/providers/categories/"),
  },
  property_providers: {
    list: (propertyId: number | string) =>
      byEndpoint(`landlord/properties/${propertyId}/providers/`),
    detail: (propertyId: number | string, providerId: number) =>
      byEndpoint(`landlord/properties/${propertyId}/providers/${providerId}/`),
  },
  providers: {
    list: byEndpoint("landlord/providers/"),
    detail: (id: number | string) => byEndpoint(`landlord/providers/${id}/`),
    categories: byEndpoint("landlord/providers/categories/"),
  },
  conditions: {
    list: byEndpoint("landlord/conditions/"),
    detail: (id: number) => byEndpoint(`landlord/conditions/${id}/`),
  },
  evidence: {
    mine: (tenancyId: number | string) =>
      byEndpoint(`tenant/tenancies/${tenancyId}/condition-evidence/`),
    withdraw: (tenancyId: number | string, id: number) =>
      byEndpoint(
        `tenant/tenancies/${tenancyId}/condition-evidence/${id}/cancel/`,
      ),
    unit: byEndpoint("landlord/condition-evidence/"),
    answer: (id: number, action: "approve" | "reject") =>
      byEndpoint(`landlord/condition-evidence/${id}/${action}/`),
    escalate_mine: (tenancyId: number | string, id: number) =>
      byEndpoint(
        `tenant/tenancies/${tenancyId}/condition-evidence/${id}/escalate/`,
      ),
    escalate_landlord: (id: number) =>
      byEndpoint(`landlord/condition-evidence/${id}/escalate/`),
  },
  reviewCases: {
    list: byEndpoint("admin/review-cases/"),
    decide: (id: number, action: "approve" | "reject") =>
      byEndpoint(`admin/review-cases/${id}/${action}/`),
  },
  maintenance: {
    list: byEndpoint("maintenance/"),
    categories: byEndpoint("maintenance/categories/"),
    detail: (id: number | string) => byEndpoint(`maintenance/${id}/`),
    action: (id: number, path: string) =>
      byEndpoint(`maintenance/${id}/${path}/`),
    respond: (id: number, proposalId: number, answer: string) =>
      byEndpoint(`maintenance/${id}/closure/${proposalId}/${answer}/`),
  },
  admin_maintenance: {
    list: byEndpoint("admin/maintenance/"),
    detail: (id: number | string) => byEndpoint(`admin/maintenance/${id}/`),
    action: (id: number, path: string) =>
      byEndpoint(`admin/maintenance/${id}/${path}/`),
  },
  notifications: {
    list: byEndpoint("notifications/"),
    unread_count: byEndpoint("notifications/unread-count/"),
    read_all: byEndpoint("notifications/read-all/"),
    read: (id: number) => byEndpoint(`notifications/${id}/read/`),
  },
  tenancies: tenancyApi("tenancies"),
  landlord_tenancies: tenancyApi("landlord/tenancies"),
  tenant_tenancies: {
    list: byEndpoint("tenant/tenancies/"),
    detail: (id: number | string) => byEndpoint(`tenant/tenancies/${id}/`),
    respond_terms: (id: number, changeId: number, answer: string) =>
      byEndpoint(`tenant/tenancies/${id}/changes/${changeId}/${answer}/`),
    providers: (id: number | string) =>
      byEndpoint(`tenant/tenancies/${id}/providers/`),
    request_housemate: (id: number) =>
      byEndpoint(`tenant/tenancies/${id}/invitations/`),
    withdraw_housemate: (id: number, invitationId: number) =>
      byEndpoint(
        `tenant/tenancies/${id}/invitations/${invitationId}/withdraw/`,
      ),
  },
  tenant_invitations: {
    list: byEndpoint("tenant/invitations/"),
    accept_by_id: (id: number) =>
      byEndpoint(`tenant/invitations/${id}/accept/`),
    accept: byEndpoint("tenant/invitations/accept/"),
    preview: byEndpoint("tenant/invitations/preview/"),
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
    reset_authenticator: (id: number | string) =>
      byEndpoint(`users/${id}/reset-authenticator/`),
    resend_authenticator_notice: (id: number | string) =>
      byEndpoint(`users/${id}/resend-authenticator-notice/`),
  },
  auth: {
    sign_up: byEndpoint("auth/sign-up/"),
    verify_email: byEndpoint("auth/verify-email/"),
    resend_verification: byEndpoint("auth/resend-verification/"),
    sign_in: byEndpoint("auth/sign-in/"),
    forgot_password: byEndpoint("auth/forgot-password/"),
    reset_password: byEndpoint("auth/reset-password/"),
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
