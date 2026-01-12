from django.db import models
from django.utils.text import slugify
from django.conf import settings
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:100]
            slug = base
            i = 1
            while ProductCategory.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    category=models.ForeignKey(ProductCategory, on_delete=models.SET_NULL,null=True,blank=True,related_name='products_category')
    currency=models.CharField(max_length=10, default='USD')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    thumbnail = models.ImageField(upload_to='products/')
    contact_phone = models.CharField(max_length=32, blank=True)
    whatsapp_number = models.CharField(max_length=32, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:180]
            slug = base
            i = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base}-{(self.description)[:10]}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
class ProductImages(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_images')
    image=models.ImageField(upload_to='Product_images/')
    
    def __str__(self):
        return self.product.title
class Ads(models.Model):
    image = models.ImageField(upload_to='ads/',blank=True, null=True)
    text = models.TextField()
    active = models.BooleanField(default=True)  # Admin can turn ad ON/OFF
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ad #{self.id}"
class HomepageBanner(models.Model):
    image = models.ImageField(upload_to='banners/')
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f"Banner #{self.id}"
class LoginBanner(models.Model):
    image = models.ImageField(upload_to='login_banners/')
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f"Login Banner #{self.id}"