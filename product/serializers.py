from rest_framework import serializers
from product import models as product_models
import base64

class ProductImageSerializer(serializers.ModelSerializer):
    image_base64 = serializers.SerializerMethodField()

    class Meta:
        model = product_models.ProductImage
        fields = ['image_base64']

    def get_image_base64(self, obj):
        with open(obj.image.path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = product_models.Product
        fields = '__all__'
        extra_fields = ['uploaded_images']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = product_models.Product.objects.create(**validated_data)
        
        for image in uploaded_images:
            product_models.ProductImage.objects.create(product=product, image=image)
        
        return product

class ProductDeleteSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=16, help_text="Codice del prodotto da eliminare")
