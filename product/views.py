from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from product import serializers as product_serializers
from product import models as product_models

class ProductView(APIView):
    @extend_schema(
        request=product_serializers.ProductSerializer,
        responses=product_serializers.ProductSerializer,
        description="Create a new product with optional images."
    )
    def post(self, request):
        serializer = product_serializers.ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(product_serializers.ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses=product_serializers.ProductSerializer(many=True),
        description="Retrieve the list of all products with images."
    )
    def get(self, request):
        products = product_serializers.ProductSerializer(product_models.Product.objects.all(), many=True)
        return Response(products.data, status=status.HTTP_200_OK)


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