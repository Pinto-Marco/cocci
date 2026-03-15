from tokenize import triple_quoted
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter
from product import serializers as product_serializers
from product import models as product_models
from orders import models as orders_models
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Q, Case, When, Value, IntegerField

import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from rest_framework.pagination import PageNumberPagination


class ProductView(APIView):
    @extend_schema(
        request=product_serializers.ProductSerializer,
        responses=product_serializers.ProductSerializer,
        description="Create a new product with optional images and associate it with a category.",
    )
    def post(self, request):
        serializer = product_serializers.ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                product_serializers.ProductSerializer(product).data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="page", type=int, description="Page number", required=False
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                description="Number of items per page",
                required=False,
            ),
            OpenApiParameter(
                name="tags",
                type=str,
                description="Comma-separated list of tag IDs",
                required=False,
            ),
            OpenApiParameter(
                name="order_by_price",
                type=str,
                description='Order by price: "asc" or "desc"',
                required=False,
            ),
        ],
        responses=product_serializers.ProductSerializer(many=True),
        description="Retrieve the list of all products with images, with optional filtering and ordering.",
    )
    def get(self, request):
        # Get query parameters
        tag_ids = request.query_params.get("tags", "").split(",")
        order_by_price = request.query_params.get("order_by_price", None)

        # Start with all products
        queryset = product_models.Product.objects.all().order_by("-id")

        # Filter by tags if provided
        if tag_ids and tag_ids[0]:  # Check if there are any tag IDs
            # Support both tag names (frontend) and tag IDs (tests)
            q_filter = Q(producttag__tag__name__in=tag_ids) | Q(producttag__tag__id__in=[t for t in tag_ids if t.isdigit()])
            queryset = queryset.filter(q_filter).distinct()

        # Order by price if specified
        sort = request.query_params.get("sort", None)
        if sort:
            if sort == "price_asc":
                queryset = queryset.order_by("price")
            elif sort == "price_desc":
                queryset = queryset.order_by("-price")
            elif sort == "year_asc":
                queryset = queryset.order_by("code")
            elif sort == "year_desc":
                queryset = queryset.order_by("-code")
        elif order_by_price:  # Legacy support
            order_field = "price" if order_by_price.lower() == "asc" else "-price"
            queryset = queryset.order_by(order_field)

        # Apply pagination using DRF's PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get("page_size", 12))
        
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        if paginated_queryset is not None:
            serializer = product_serializers.ProductSerializer(paginated_queryset, many=True)
            response = paginator.get_paginated_response(serializer.data)
            # Add extra metadata for numbered pagination
            response.data["current_page"] = paginator.page.number
            response.data["total_pages"] = paginator.page.paginator.num_pages
            return response

        # Fallback if pagination is not applied
        serializer = product_serializers.ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductDeleteView(APIView):
    @extend_schema(
        request=product_serializers.ProductDeleteSerializer,
        responses={200: "Product deleted successfully", 404: "Product not found"},
        description="Elimina un prodotto tramite il codice",
    )
    def post(self, request):
        serializer = product_serializers.ProductDeleteSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data["code"]
            try:
                product = product_models.Product.objects.get(code=code)
                return Response(
                    {
                        "error": "Product deleted successfully"
                    },  # Wait, success message should vary? No, keep message or use status.
                    # Standard: 200/204 for success. 200 with message.
                    {"message": "Product deleted successfully"},
                    status=status.HTTP_200_OK,
                )
            except product_models.Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
                )
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


# class CategoryListView(APIView):
#     @extend_schema(
#         responses=product_serializers.CategorySerializer(many=True),
#         description="Retrieve the list of all categories."
#     )
#     def get(self, request):
#         categories = product_models.Category.objects.all()
#         serializer = product_serializers.CategorySerializer(categories, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class ProductTransferView(APIView):
    def get(self, request, code):
        try:
            product = product_models.Product.objects.get(code=code)
        except product_models.Product.DoesNotExist:
            return Response(
                {"error": "Product with specified code does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.is_available = not product.is_available
        product.save()

        return Response(
            {
                "message": "Product status updated successfully.",
                "product": {
                    "code": product.code,
                    "title": product.title,
                    "is_available": product.is_available,
                },
            },
            status=status.HTTP_200_OK,
        )


class ProductDetailsUpdateView(APIView):
    # @extend_schema(
    #     request=product_serializers.ProductSerializer,
    # )
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = product_serializers.ProductSerializer

    def get(self, request, code):
        product = get_object_or_404(product_models.Product, code=code)
        serializer = product_serializers.ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags = product_models.Tag.objects.all()
        return Response([tag.name for tag in tags], status=status.HTTP_200_OK)


class ProductSearchView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                type=str,
                description="Search query for product title and description",
                required=True,
            ),
            OpenApiParameter(
                name="limit",
                type=int,
                description="Maximum number of results to return (1-20)",
                required=False,
            ),
        ],
        responses=product_serializers.ProductSearchSerializer(many=True),
        description="Search products by title and description with lightweight results.",
    )
    def get(self, request):
        query = request.query_params.get("q", "").strip()

        try:
            limit = int(request.query_params.get("limit", 8))
        except (TypeError, ValueError):
            limit = 8

        limit = max(1, min(limit, 20))

        if not query:
            return Response({"results": []}, status=status.HTTP_200_OK)

        queryset = (
            product_models.Product.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            .annotate(
                search_rank=Case(
                    When(title__istartswith=query, then=Value(0)),
                    When(title__icontains=query, then=Value(1)),
                    When(description__icontains=query, then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            )
            .order_by("search_rank", "title", "code")[:limit]
        )

        serializer = product_serializers.ProductSearchSerializer(queryset, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


def get_or_create_cart_id(request):
    if "cart_id" not in request.session:
        request.session["cart_id"] = (
            request.session.session_key or request.session.create()
        )
    return request.session["cart_id"]


@extend_schema(exclude=True)
@ensure_csrf_cookie
def StoreView(request):
    return render(request, "vue_base.html")


def product_detail_view(request, product_code):
    product = get_object_or_404(product_models.Product, code=product_code)
    images = product_models.ProductImage.objects.filter(product=product)
    # For the template, we might want to pass image URLs or base64 data
    # Assuming ProductImage model has an 'image' field (ImageField)
    image_urls = [img.image for img in images]

    context = {
        "product": product,
        "image_urls": image_urls,  # Or pass the images queryset directly if template handles it
    }
    return render(request, "product_detail.html", context)


@ensure_csrf_cookie
def HomeView(request):
    return render(request, "vue_base.html")


@ensure_csrf_cookie
def ContactsView(request):
    return render(request, "vue_base.html")


@extend_schema(exclude=True)
@ensure_csrf_cookie
def ProductDetailPageView(request, code):
    return render(request, "vue_base.html")
