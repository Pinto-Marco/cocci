from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from product import serializers as product_serializers
from product import models as product_models
from django.shortcuts import render
from drf_spectacular.openapi import OpenApiParameter

import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class ProductView(APIView):
    @extend_schema(
        request=product_serializers.ProductSerializer,
        responses=product_serializers.ProductSerializer,
        description="Create a new product with optional images and associate it with a category."
    )
    def post(self, request):
        serializer = product_serializers.ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(product_serializers.ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='page', type=int, description='Page number', required=False),
            OpenApiParameter(name='page_size', type=int, description='Number of items per page', required=False),
            OpenApiParameter(name='tags', type=str, description='Comma-separated list of tag IDs', required=False),
            OpenApiParameter(name='order_by_price', type=str, description='Order by price: "asc" or "desc"', required=False),
        ],
        responses=product_serializers.ProductSerializer(many=True),
        description="Retrieve the list of all products with images, with optional filtering and ordering."
    )
    def get(self, request):
        # Get query parameters
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        tag_ids = request.query_params.get('tags', '').split(',')
        order_by_price = request.query_params.get('order_by_price', None)

        # Start with all products
        queryset = product_models.Product.objects.all()

        # Filter by tags if provided
        if tag_ids and tag_ids[0]:  # Check if there are any tag IDs
            queryset = queryset.filter(producttag__tag_id__in=tag_ids).distinct()

        # Order by price if specified
        if order_by_price:
            order_field = 'price' if order_by_price.lower() == 'asc' else '-price'
            queryset = queryset.order_by(order_field)

        # Apply pagination
        paginator = Paginator(queryset, page_size)
        try:
            products_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            products_page = paginator.page(paginator.num_pages)

        # Serialize the data
        serializer = product_serializers.ProductSerializer(products_page, many=True)

        # Prepare pagination data
        response_data = {
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'next': products_page.has_next(),
            'previous': products_page.has_previous(),
            'results': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ProductDeleteView(APIView):
    @extend_schema(
        request=product_serializers.ProductDeleteSerializer,
        responses={200: "Product deleted successfully", 404: "Product not found"},
        description="Elimina un prodotto tramite il codice"
    )
    def post(self, request):
        serializer = product_serializers.ProductDeleteSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                product = product_models.Product.objects.get(code=code)
                product.delete()
                return Response({"detail": "Product deleted successfully"}, status=status.HTTP_200_OK)
            except product_models.Product.DoesNotExist:
                return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
                {"error": "Il prodotto con il codice specificato non esiste."},
                status=status.HTTP_404_NOT_FOUND
            )

        product.out = not product.out
        product.save()

        return Response(
            {
                "message": "Lo stato del prodotto è stato aggiornato.",
                "product": {
                    "code": product.code,
                    "title": product.title,
                    "out": product.out
                }
            },
            status=status.HTTP_200_OK
        )
    
class ProductDetailsUpdateView(APIView):
    @extend_schema(
        request=product_serializers.ProductSerializer,
        responses=product_serializers.ProductSerializer,
        description="Retrieve product details."
    )
    def get(self, request, code):
        try:
            product = product_models.Product.objects.get(code=code)
        except product_models.Product.DoesNotExist:
            return Response(
                {"error": "Il prodotto con il codice specificato non esiste."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = product_serializers.ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def put(self, request, code):
    #     try:
    #         product = product_models.Product.objects.get(code=code)
    #     except product_models.Product.DoesNotExist:
    #         return Response(
    #             {"error": "Il prodotto con il codice specificato non esiste."},
    #             status=status.HTTP_404_NOT_FOUND
    #         )

    #     serializer = product_serializers.ProductSerializer(product, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def StoreView(request):
    tags = request.GET.get('tags')
    if tags:
        tags = tags.split(',')
        print(tags)
        product_list = product_models.Product.objects.filter(producttag__tag__name__in=tags).distinct().order_by('id')
    else:
        product_list = product_models.Product.objects.all().distinct().order_by('id')

    paginator = Paginator(product_list, 12)  # Show 5 products per page

    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    products_serialized = product_serializers.ProductSerializer(products, many=True)

    refined_products = []
    for product in products_serialized.data:
        refined_product = {
            'title': product['title'],
            'price': product['price'],
            'code': product['code'],
            'out': product['out'],
            'is_available': product['is_available'],
            'description': product['description'],
        }
        if 'images' in product.keys(): # Or .all() depending on relation
            # Assuming product.images is a related manager for image objects
            # and each image object has an 'image_base64' attribute.
            image_base64_list = [img['image_base64'] for img in product['images']]
            refined_product['images_json_data'] = json.dumps(image_base64_list)
        else:
            refined_product['images_json_data'] = "[]"

        refined_products.append(refined_product)

    tags = product_models.Tag.objects.all()

    tags = [tag.name for tag in tags]

    return render(request, 'store.html', context={'products': refined_products, 'tags': tags, 'page_obj': products})


def HomeView(request):
    return render(request, 'home.html')

def ContactsView(request):
    return render(request, 'contacts.html')