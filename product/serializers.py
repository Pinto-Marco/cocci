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
    # category_id = serializers.IntegerField(required=False)
    # category_name = serializers.CharField(required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = product_models.Product
        fields = ['id', 'code', 'price', 'title', 'description', 'barcode', 'out', 'category_id', 'category_name', 'tags', 'images', 'uploaded_images']
        # fields = '__all__'

        # extra_fields = ['uploaded_images', 'category_id', 'category_name']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        # category_id = validated_data.pop('category_id', None)
        # category_name = validated_data.pop('category_name', None)
        tags = validated_data.pop('tags', None)

        # if category_id:
        #     category = product_models.Category.objects.get(id=category_id)
        # elif category_name:
        #     category, _ = product_models.Category.objects.get_or_create(name=category_name)
        # else:
        #     raise serializers.ValidationError("Devi fornire un 'category_id' o un 'category_name'.")

        product = product_models.Product.objects.create(**validated_data)

        # product_models.ProductCategory.objects.create(product=product, category=category)

        if tags:
            for tag in tags:
                if not product_models.Tag.objects.filter(name=tag).exists():
                    new_tag = product_models.Tag.objects.get_or_create(name=tag)
                    product_models.ProductTag.objects.create(tag=new_tag, product=product)
                else:
                    old_tag = product_models.Tag.objects.get(name=tag)
                    if not product_models.ProductTag.objects.filter(tag=old_tag, product=product).exists():
                        product_models.ProductTag.objects.create(tag=old_tag, product=product)

        for image in uploaded_images:
            product_models.ProductImage.objects.create(product=product, image=image)
        
        return product

    # def get_category_name(self, obj):
    #     if obj.get_category() is None:
    #         return None
    #     return obj.get_category().name
    
    # def get_category_id(self, obj):
    #     if obj.get_category() is None:
    #         return None
    #     return obj.get_category().id
    
    def get_tags(self, obj):
        if obj.get_tags() is None:
            return []
        return obj.get_tags()


    
# class ProductSerializer(serializers.ModelSerializer):
#     images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')
#     uploaded_images = serializers.ListField(
#         child=serializers.ImageField(), write_only=True, required=False
#     )

#     class Meta:
#         model = product_models.Product
#         fields = '__all__'
#         extra_fields = ['uploaded_images']

#     def create(self, validated_data):
#         uploaded_images = validated_data.pop('uploaded_images', [])
#         product = product_models.Product.objects.create(**validated_data)
        
#         for image in uploaded_images:
#             product_models.ProductImage.objects.create(product=product, image=image)
        
#         return product

class ProductDeleteSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=16, help_text="Codice del prodotto da eliminare")

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = product_models.Category
#         fields = ['id', 'name']