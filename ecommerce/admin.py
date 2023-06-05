from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Coupon)
admin.site.register(CouponUsed)
admin.site.register(Reviews)
admin.site.register(EcommerceCart)
admin.site.register(News)
admin.site.register(UserProfile)
admin.site.register(Favorite)
admin.site.register(Comment)
admin.site.register(Shop)
admin.site.register(ShopDetail)
admin.site.register(Rating)

