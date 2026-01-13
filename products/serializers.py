from rest_framework import serializers
from .models import Product,ProductCategory,ProductImages,Ads,HomepageBanner,LoginBanner,VideoAds

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']
class ProductImagesSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImages
        fields = ['id', 'image', 'image_url']
        read_only_fields = ['image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        if obj.image:
            return obj.image.url
        return None
class ProductSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    product_images = ProductImagesSerializer(many=True, read_only=True)
    uploaded_by = serializers.CharField(source="user.username", read_only=True)
    thumbnail = serializers.ImageField(required=False)
    category_data=ProductCategorySerializer(source='category', read_only=True)
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'price','currency',
            'thumbnail', 'thumbnail_url', 'contact_phone',
            'whatsapp_number', 'location', 'views','active', 'created_at','category_data',
            'category', 'product_images', 'uploaded_by'
        ]
        read_only_fields = ['slug', 'created_at', 'thumbnail_url', 'uploaded_by']

    def create(self, validated_data):
        # 1️⃣ Extract images from request.FILES
        request = self.context.get("request")
        images = request.FILES.getlist("images")

        # 2️⃣ Create product
        product = Product.objects.create(**validated_data)

        # 3️⃣ Save product images into ProductImages model
        for img in images:
            ProductImages.objects.create(product=product, image=img)

        return product

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        if obj.thumbnail:
            return obj.thumbnail.url
        return None


class AdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ads
        fields = "__all__"
class HomeBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepageBanner
        fields = "__all__"
class LoginBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginBanner
        fields = "__all__"
class VideoAdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoAds
        fields = "__all__"