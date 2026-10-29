ADMIN = "ADMIN"
LANDLORD = "LANDLORD"
TENANT = "TENANT"

ROLES = [
    (ADMIN, "Admin"),
    (LANDLORD, "Landlord"),
    (TENANT, "Tenant"),
]

PARTIES = {LANDLORD, TENANT}
EVERYONE = {ADMIN, LANDLORD, TENANT}

PERMISSIONS = [
    ("accounts.update_profile", "Update own profile", "accounts", EVERYONE),
    ("accounts.manage", "Suspend and reactivate accounts", "accounts", {ADMIN}),
    ("access.manage", "Grant and revoke roles and permissions", "access", {ADMIN}),
    ("access.view_hidden_records", "View hidden records", "access", set()),
    ("properties.view", "View private property details", "properties", EVERYONE),
    ("properties.create", "Create properties", "properties", {LANDLORD}),
    ("properties.update", "Edit property and unit details", "properties", {LANDLORD}),
    ("properties.manage_owners", "Add and end co-owners", "properties", {LANDLORD}),
    ("properties.publish", "Change listing status", "properties", {LANDLORD}),
    ("tenancies.view", "View tenancies", "tenancies", EVERYONE),
    ("tenancies.create", "Create tenancies", "tenancies", {LANDLORD}),
    ("tenancies.update", "Edit tenancy details", "tenancies", {LANDLORD}),
    ("tenancies.manage_parties", "Add and remove tenants", "tenancies", {LANDLORD}),
    ("files.upload", "Upload files", "files", PARTIES),
    ("files.download", "Download files", "files", EVERYONE),
    ("conditions.view", "View condition records", "conditions", EVERYONE),
    ("conditions.submit_baseline", "Submit baseline condition", "conditions", {LANDLORD}),
    ("conditions.submit_update", "Submit later condition evidence", "conditions", PARTIES),
    ("reviews.view", "View review cases", "reviews", EVERYONE),
    ("reviews.submit", "Submit change and correction requests", "reviews", PARTIES),
    ("reviews.decide", "Approve, reject or dispute as opposite side", "reviews", PARTIES),
    ("reviews.escalate", "Escalate a dispute to Admin", "reviews", PARTIES),
    ("reviews.request_removal", "Request data removal", "reviews", PARTIES),
    ("reviews.admin_review", "Decide Admin-routed cases", "reviews", {ADMIN}),
    ("reviews.review_removal", "Decide data removal requests", "reviews", {ADMIN}),
    ("maintenance.view", "View maintenance issues", "maintenance", EVERYONE),
    ("maintenance.report", "Report an issue", "maintenance", PARTIES),
    ("maintenance.confirm_start", "Confirm work started", "maintenance", PARTIES),
    ("maintenance.propose_closure", "Propose closing an issue", "maintenance", PARTIES),
    ("maintenance.review_closure", "Approve or reject a closure", "maintenance", PARTIES),
    (
        "maintenance.close_vacant",
        "Close directly with no current tenant",
        "maintenance",
        {LANDLORD},
    ),
    ("maintenance.record_assignment", "Record provider engagement", "maintenance", PARTIES),
    ("documents.view", "View documents", "documents", EVERYONE),
    ("documents.publish", "Upload document versions", "documents", {LANDLORD}),
    ("documents.confirm", "Confirm or flag a document", "documents", {TENANT}),
    ("providers.view", "View service providers", "providers", EVERYONE),
    ("providers.manage", "Manage providers and recommendations", "providers", {LANDLORD}),
    ("providers.manage_categories", "Manage service categories", "providers", {ADMIN}),
    ("communications.view", "View communication logs", "communications", EVERYONE),
    ("communications.log", "Log an external communication", "communications", PARTIES),
]
