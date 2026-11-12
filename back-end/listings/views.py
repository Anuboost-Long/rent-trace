from django.http import FileResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from common.pagination import PagePagination
from listings import dtos, resources, services

PHOTO_CACHE = "public, max-age=3600"


class PublicBrowseView(APIView):
    """Anyone can browse. These views never see who is asking and only ever return public fields."""

    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "public_browse"


class ListingsView(PublicBrowseView):
    @extend_schema(
        operation_id="listings_list",
        parameters=[dtos.ListingQueryDto],
        responses=resources.ListingPageResource,
    )
    def get(self, request):
        serializer = dtos.ListingQueryDto(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data
        listings = services.list_listings(
            search=services.ListingSearch(
                q=query.get("q"),
                state=query.get("state"),
                suburb=query.get("suburb"),
                property_type=query.get("type"),
                min_rent=query.get("min_rent"),
                max_rent=query.get("max_rent"),
                sort=query["sort"],
            )
        )
        paginator = PagePagination()
        page = paginator.paginate_queryset(listings, request, view=self)
        return paginator.get_paginated_response(
            resources.ListingSummaryResource(page, many=True).data
        )


class PlacesView(PublicBrowseView):
    @extend_schema(operation_id="listings_places", responses=resources.PlaceResource(many=True))
    def get(self, request):
        return Response(resources.PlaceResource(services.list_places(), many=True).data)


class ListingDetailView(PublicBrowseView):
    @extend_schema(operation_id="listings_get", responses=resources.ListingDetailResource)
    def get(self, request, listing_id):
        listing = services.get_listing(listing_id=listing_id)
        return Response(resources.ListingDetailResource(listing).data)


class ListingPhotoView(PublicBrowseView):
    @extend_schema(
        operation_id="listings_photo", responses={(200, "application/octet-stream"): bytes}
    )
    def get(self, request, listing_id, file_id):
        stored, content = services.open_listing_photo(listing_id=listing_id, file_id=file_id)
        response = FileResponse(content, content_type=stored.mime_type)
        response["Cache-Control"] = PHOTO_CACHE
        return response
