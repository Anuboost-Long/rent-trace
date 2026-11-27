const SAFE_PATH = /^[a-z0-9\-/]+$/;
const ALLOWED = [
  /^tenant\/tenancies\/\d+\/(condition-evidence|condition-corrections|removal-requests|documents)\//,
  /^landlord\/(condition-evidence|condition-corrections|removal-requests|documents)\//,
  /^admin\/(review-cases|condition-corrections|removal-requests|documents|condition-evidence)\//,
];

export const isAllowedPath = (path: string) =>
  SAFE_PATH.test(path) && ALLOWED.some((pattern) => pattern.test(path));
