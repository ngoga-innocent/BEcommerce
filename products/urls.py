from rest_framework.routers import DefaultRouter
from .views import ProductViewSet,ProductCategoryViewSet,AdViewSet,HomeBannerViewSet,LoginBannerViewSet,VideoAdsViewSet,ProductViewIncrement
from django.urls import path


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='categories')
router.register(r'ads', AdViewSet, basename='ads')
router.register(r'home-banners', HomeBannerViewSet, basename='home-banners')
router.register(r'login-banners', LoginBannerViewSet, basename='login-banners')
router.register(r'video-ads', VideoAdsViewSet, basename='video-ads')
urlpatterns = router.urls
urlpatterns += [
    # urls.py
path("products/<slug:slug>/view/", ProductViewIncrement.as_view()),

]