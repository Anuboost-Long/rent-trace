from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ClampedPaginator(Paginator):
    """A page number that is too high or not a number gives the last or first page, not a 404."""

    def page(self, number):
        try:
            number = self.validate_number(number)
        except PageNotAnInteger:
            number = 1
        except EmptyPage:
            number = self.num_pages
        return super().page(number)


class PagePagination(PageNumberPagination):
    django_paginator_class = ClampedPaginator
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        paginator = self.page.paginator
        return Response(
            {
                "count": paginator.count,
                "page": self.page.number,
                "page_size": paginator.per_page,
                "total_pages": paginator.num_pages,
                "results": data,
            }
        )
