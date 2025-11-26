from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, ProductCategory,ProductImages,Ads
from .serializers import ProductSerializer, ProductCategorySerializer,AdsSerializer


# -------------------- Product ViewSet --------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = "slug"

    def get_permissions(self):
        # Admin only for create/update/delete
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        # Read actions open to anyone
        return [permissions.AllowAny()]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        

        



# -------------------- Product Category ViewSet --------------------
class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    lookup_field = 'slug'

    def get_permissions(self):
        # Admin only for create/update/delete
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        # Read actions open to anyone
        return [permissions.AllowAny()]

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Returns products for a given category slug
        """
        category = self.get_object()
        print(category)
        products = Product.objects.filter(category=category)
        print(products)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
class AdViewSet(viewsets.ModelViewSet):
    queryset = Ads.objects.all().order_by('-created_at')
    serializer_class = AdsSerializer
    parser_classes = (MultiPartParser, FormParser)
    def get_queryset(self):
        # If called from the website/public view, return only active ads
        if self.request.user.is_staff:
            # Admin sees all ads
            return Ads.objects.all().order_by("-active","-id")
        else:
            # Public view: only active ad
            return Ads.objects.filter(active=True).order_by("-id")
    def perform_update(self, serializer):
        active = serializer.validated_data.get("active")
        ad = serializer.instance
        if active:
            # Deactivate all other ads
            Ads.objects.exclude(id=ad.id).update(active=False)
        serializer.save()
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
