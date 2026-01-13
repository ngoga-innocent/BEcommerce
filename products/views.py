from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Product, ProductCategory,Ads,HomepageBanner,LoginBanner,VideoAds,ProductView
from .serializers import ProductSerializer, ProductCategorySerializer,AdsSerializer,HomeBannerSerializer,LoginBannerSerializer,VideoAdsSerializer
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import F
from django.db import IntegrityError

from django.utils import timezone

from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Product, ProductView
# -------------------- Product ViewSet --------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = "slug"

    # Custom permission logic
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]  # Only logged-in users can create
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]  # Owner or admin check in perform_* methods
        return [permissions.AllowAny()]  # Anyone can list/view

    # Ensure only owner or admin can modify/delete
    def perform_update(self, serializer):
        instance = serializer.instance
        if self.request.user != instance.user and not self.request.user.is_staff:
            raise PermissionDenied("You cannot edit someone else's product.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.user and not self.request.user.is_staff:
            raise PermissionDenied("You cannot delete someone else's product.")
        instance.delete()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Endpoint to get logged-in user's products
    

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my(self, request):
        """
        Return products of the logged-in user
        """
        products = Product.objects.filter(user=request.user).order_by("-created_at")
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
        

        



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
class HomeBannerViewSet(viewsets.ModelViewSet):
    queryset=HomepageBanner.objects.all().order_by('-id')
    serializer_class=HomeBannerSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
class LoginBannerViewSet(viewsets.ModelViewSet):
    queryset=LoginBanner.objects.all().order_by('-id')
    serializer_class=LoginBannerSerializer
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
class VideoAdsViewSet(viewsets.ModelViewSet):
    queryset = VideoAds.objects.all().order_by('-created_at')
    serializer_class = VideoAdsSerializer
    parser_classes = (MultiPartParser, FormParser)
    def get_queryset(self):
        # If called from the website/public view, return only active video ads
        if self.request.user.is_staff:
            # Admin sees all video ads
            return VideoAds.objects.all().order_by("-active","-id")
        else:
            # Public view: only active video ads
            return VideoAds.objects.filter(active=True).order_by("-id")
    def perform_update(self, serializer):
        active = serializer.validated_data.get("active")
        video_ad = serializer.instance
        if active:
            # Deactivate all other video ads
            VideoAds.objects.exclude(id=video_ad.id).update(active=False)
        serializer.save()
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]
def get_client_ip(request):
    """
    Safely get client IP even behind proxy / load balancer
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class ProductViewIncrement(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        
        try:
            # 1️⃣ Get product safely
            product = get_object_or_404(Product, slug=slug)

            # 2️⃣ Extract request metadata
            ip = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            user = request.user if request.user.is_authenticated else None
            print(ip, user_agent, user)
            if not ip:
                return Response(
                    {"detail": "Unable to determine client IP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3️⃣ Check if view already exists
            already_viewed = ProductView.objects.filter(
                product=product,
                user=user,
                ip_address=ip,
                user_agent=user_agent,
            ).exists()

            if already_viewed:
                return Response(
                    {"success": True, "counted": False},
                    status=status.HTTP_200_OK,
                )

            # 4️⃣ Create view + increment counter (atomic)
            ProductView.objects.create(
                product=product,
                user=user,
                ip_address=ip,
                user_agent=user_agent,
                created_at=timezone.now(),
            )

            Product.objects.filter(id=product.id).update(
                views=F("views") + 1
            )

            return Response(
                {"success": True, "counted": True},
                status=status.HTTP_201_CREATED,
            )

        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except IntegrityError:
            # Handles race conditions / unique constraints
            return Response(
                {"success": True, "counted": False},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Catch-all (log this in production!)
            print("Product view error:", str(e))

            return Response(
                {"detail": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )