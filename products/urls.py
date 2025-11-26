from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,ProductCategoryViewSet,AdViewSet


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='categories')
router.register(r'ads', AdViewSet, basename='ads')

urlpatterns = router.urls