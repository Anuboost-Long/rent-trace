from rest_framework.exceptions import APIException


class HasTenancies(APIException):
    status_code = 409
    default_detail = "This can't be removed while it has tenancies."
    default_code = "has_tenancies"
