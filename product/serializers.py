from rest_framework import serializers
from product import models as product_models
import base64

class ProductImageSerializer(serializers.ModelSerializer):
    image_base64 = serializers.SerializerMethodField()

    class Meta:
        model = product_models.ProductImage
        fields = ['image_base64']

    def get_image_base64(self, obj):
        print(obj.image.path)
        with open(obj.image.path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
        
class ProductImageUrlSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = product_models.ProductImage
        fields = ['image_url']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None
        
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = product_models.Tag
        fields = ['name']
        
        
class ProductTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer(read_only=True)
    class Meta:
        model = product_models.ProductTag
        fields = ['tag']
        
        
class ListProductSerializer(serializers.ModelSerializer):
    images = ProductImageUrlSerializer(many=True, read_only=True, source='productimage_set')
    tags = ProductTagSerializer(many=True, read_only=True, source='product_tags')
    
    class Meta:
        model = product_models.Product
        fields = ['id', 'code', 'price', 'title', 'description', 'barcode', 'out', 'images', 'tags', 'penalty', 'is_available']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageUrlSerializer(many=True, read_only=True, source='productimage_set')
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = product_models.Product
        fields = ['id', 'code', 'price', 'title', 'description', 'barcode', 'out', 'tags', 'images', 'uploaded_images', 'penalty', 'is_available']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        tags = validated_data.pop('tags', [])

        # Creiamo il prodotto
        product = product_models.Product.objects.create(**validated_data)

        # Assicuriamoci che il prodotto sia salvato prima di creare relazioni
        product.save()

        # Gestione dei tag in modo più efficiente
        tag_objects = []
        for tag in tags:
            tag_obj, _ = product_models.Tag.objects.get_or_create(name=tag)
            tag_objects.append(tag_obj)

        # Creiamo le relazioni tra prodotto e tag
        product_models.ProductTag.objects.bulk_create(
            [product_models.ProductTag(tag=tag, product=product) for tag in tag_objects],
            ignore_conflicts=True  # Evita errori in caso di duplicati
        )

        # Creiamo le immagini
        product_models.ProductImage.objects.bulk_create(
            [product_models.ProductImage(product=product, image=image) for image in uploaded_images]
        )

        return product
    
    def get_tags(self, obj):
        if obj.get_tags() is None:
            return []
        return obj.get_tags()
    
    
class ProductUpdateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    
    class Meta:
        model = product_models.Product
        fields = ['price', 'title', 'description', 'tags', 'uploaded_images', 'penalty', 'is_available']
        extra_kwargs = {
            'price': {'required': False},
            'title': {'required': False},
            'description': {'required': False},
            'tags': {'required': False},
            'uploaded_images': {'required': False},
            'penalty': {'required': False},
            'is_available': {'required': False}
        }
        
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        tags = validated_data.pop('tags', [])
        # Aggiorniamo i campi del prodotto
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Aggiorniamo le immagini
        for image in uploaded_images:
            product_models.ProductImage.objects.create(product=instance, image=image)
        # Aggiorniamo i tag
        if len(tags) > 0:
            old_tags = product_models.ProductTag.objects.filter(product=instance)
            for tag in tags:
                if tag not in old_tags:
                    try:
                        tag_obj = product_models.Tag.objects.get(name=tag)
                        product_models.ProductTag.objects.create(tag=tag_obj, product=instance)
                    except product_models.Tag.DoesNotExist:
                        tag_obj = product_models.Tag.objects.create(name=tag)
                        product_models.ProductTag.objects.create(tag=tag_obj, product=instance)
            
            for old_tag in old_tags:
                if old_tag not in tags:
                    old_tag.delete()
                
        instance.save()
        return instance


class ProductDeleteSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, max_length=16, help_text="Codice del prodotto da eliminare")
