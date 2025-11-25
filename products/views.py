from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, ProductCategory,ProductImages
from .serializers import ProductSerializer, ProductCategorySerializer


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
