from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,ProductCategoryViewSet


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='categories')

urlpatterns = router.urls