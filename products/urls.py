from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,ProductCategoryViewSet,AdViewSet,HomeBannerViewSet,LoginBannerViewSet


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='categories')
router.register(r'ads', AdViewSet, basename='ads')
router.register(r'home-banners', HomeBannerViewSet, basename='home-banners')
router.register(r'login-banners', LoginBannerViewSet, basename='login-banners')
urlpatterns = router.urls