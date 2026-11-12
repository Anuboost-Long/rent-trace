from rest_framework.exceptions import APIException


class PrimaryTenantTaken(APIException):
    status_code = 409
    default_detail = {"invitation": "This tenancy already has a primary tenant."}
    default_code = "primary_tenant_taken"
