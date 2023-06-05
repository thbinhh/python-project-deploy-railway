# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    """Represents an authenticated user in the system.

    Attributes:
        password (str): The hashed password of the user.
        last_login (datetime): The last login timestamp of the user.
        is_superuser (bool): Indicates whether the user has superuser privileges.
        username (str): The unique username of the user.
        last_name (str): The last name of the user.
        email (str): The email address of the user.
        is_staff (bool): Indicates whether the user has access to the admin site.
        is_active (bool): Indicates whether the user account is active.
        date_joined (datetime): The timestamp when the user joined the system.
        first_name (str): The first name of the user.
    """
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Category(models.Model):
    """Represents a category in the system.

    Attributes:
        cate_id (int): The unique identifier for the category.
        cate_parent_id (int): The ID of the parent category, if applicable.
        cate_name (str): The name of the category.
        cate_description (str): The description of the category.
        cate_status (bool): The status of the category.
        image_path (str): The path to the image associated with the category.
    """
    cate_id = models.AutoField(primary_key=True)
    cate_parent_id = models.IntegerField(blank=True, null=True)
    cate_name = models.TextField(blank=True, null=True)
    cate_description = models.TextField(blank=True, null=True)
    cate_status = models.BooleanField(blank=True, null=True)
    image_path = models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'category'


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


User = get_user_model()


class Order(models.Model):
    """Represents an order in the system.

    Attributes:
        order_id (int): The unique identifier for the order.
        user (User): The user who placed the order (foreign key reference to User model).
        ship_name (str): The name of the person to ship the order to.
        ship_address (str): The shipping address for the order.
        ship_phone (str): The phone number for the shipping contact.
        order_date (datetime): The date and time when the order was placed.
        total_price (str): The total price of the order.
        order_status (str): The status of the order.
        email (str): The email address associated with the order.
        diachi (str): The address associated with the order.
        huyen (str): The district associated with the order.
        tinh (str): The province or city associated with the order.
        payment_type (str): The payment type for the order.
    """
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    ship_name = models.TextField(blank=True, null=True)
    ship_address = models.TextField(blank=True, null=True)
    ship_phone = models.TextField(blank=True, null=True)
    order_date = models.DateTimeField(blank=True, null=True)
    total_price = models.TextField(blank=True, null=True)
    order_status = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    diachi = models.TextField(blank=True, null=True)
    huyen = models.TextField(blank=True, null=True)
    tinh = models.TextField(blank=True, null=True)
    payment_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'order'



class Product(models.Model):
    """Represents a product in the system.

    Attributes:
        product_id (int): The unique identifier for the product.
        cate_id (Category): The category of the product (foreign key reference to Category model).
        product_name (str): The name of the product.
        product_price (int): The original price of the product.
        product_price_new (int): The new price of the product, if applicable.
        product_quantity (int): The quantity of the product available.
        product_detail (str): The detailed description of the product.
        product_status (bool): The status of the product.
        rate (str): The average rating of the product.
        description (str): The description of the product.
        information (str): Additional information about the product.
        review (str): Customer reviews of the product.
        image_path (str): The path to the image associated with the product.
        type (str): The type or category of the product.
    """
    product_id = models.AutoField(primary_key=True) 
    cate_id = models.ForeignKey(Category, models.DO_NOTHING)
    product_name = models.TextField(blank=True, null=True)
    product_price = models.IntegerField(blank=True, null=True)
    product_price_new = models.IntegerField(blank=True, null=True)
    product_quantity = models.IntegerField(blank=True, null=True)
    product_detail = models.TextField(blank=True, null=True)
    product_status = models.BooleanField(blank=True, null=True)
    rate = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    information = models.TextField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    image_path = models.TextField(blank=True, null=True)
    type = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'product'

    def calculate_average_rating(self):
        """Calculate the average rating of the product.

        This function retrieves the average rating of the product from the Rating model
        and updates the 'rate' attribute of the product instance.

        Returns:
            float: The average rating of the product.
        """
        average_rating = Rating.objects.filter(product_id=self.product_id).aggregate(avg_rating=Avg('rating'))['avg_rating']
        if(average_rating == None):
            average_rating = 0
        self.rate = average_rating
        return average_rating


class Coupon(models.Model):
    """Represents a coupon in the system.

    Attributes:
        coupon (str): The coupon code.
        status (int): The status of the coupon.
        decrease (int): The amount to decrease from the total price when the coupon is applied.
    """
    coupon = models.TextField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    decrease = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'coupon'


class CouponUsed(models.Model):
    """Represents a coupon that has been used by a user in the system.

    Attributes:
        coupon (Coupon): The coupon that has been used (foreign key reference to Coupon model).
        user (User): The user who used the coupon (foreign key reference to User model).
    """
    coupon = models.ForeignKey(Coupon, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'coupon_used'


class OrderDetail(models.Model):
    """Represents the details of an order in the system.

    Attributes:
        order_detail_id (int): The unique identifier for the order detail.
        order_id (Order): The order to which the detail belongs (foreign key reference to Order model).
        product (Product): The product included in the order detail (foreign key reference to Product model).
        product_quantity (int): The quantity of the product in the order detail.
        discount (Coupon): The coupon applied to the order detail (foreign key reference to Coupon model).
        order_detail_date (datetime): The date and time when the order detail was created.
        status (str): The status of the order detail.
    """
    order_detail_id = models.AutoField(primary_key=True)
    order_id = models.ForeignKey(Order, models.DO_NOTHING)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    product_quantity = models.IntegerField(blank=True, null=True) 
    discount = models.ForeignKey(Coupon, models.DO_NOTHING)
    order_detail_date = models.DateTimeField(blank=True, null=True)
    status = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'order_detail'

    def price_order(self):
        return (self.product.product_price_new * self.product_quantity) * (100 - self.discount.decrease) / 100


class Reviews(models.Model):
    """Represents a review of a product in the system.

    Attributes:
        review_id (int): The unique identifier for the review.
        product (Product): The product being reviewed (foreign key reference to Product model).
        user (User): The user who wrote the review (foreign key reference to User model).
        comment (str): The comment or text of the review.
    """
    review_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    comment = models.TextField(blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'reviews'


class News(models.Model):
    news_id = models.AutoField(primary_key=True)
    news_title = models.TextField(blank=True, null=True)
    news_content = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'news'


class ProductImage(models.Model):
    image_id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(blank=True, null=True)
    image_path = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'product_image'


class Promotion(models.Model):
    promotion_id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    discount = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'promotion'




class UserProfile(models.Model):
    """Represents the user profile information in the system.

    Attributes:
        user (User): The user associated with the profile (foreign key reference to User model).
        bio (str): The biography or description of the user.
        age (int): The age of the user.
        address (str): The address of the user.
        phone (str): The phone number of the user.
        host (bool): Specifies if the user is a host or not.
        user_image_path (str): The path to the user's profile image.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    age = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    host = models.BooleanField(default=False)
    user_image_path = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_profile'


class Favorite(models.Model):
    """Represents a favorite product saved by a user in the system.

    Attributes:
        product (Product): The product that is favorited (foreign key reference to Product model).
        user (User): The user who favorited the product (foreign key reference to User model).
    """
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'favorite'


class Comment(models.Model):
    """Represents a comment made by a user on a product in the system.

    Attributes:
        product (Product): The product on which the comment is made (foreign key reference to Product model).
        user (User): The user who made the comment (foreign key reference to User model).
        user_profile (UserProfile): The user profile associated with the user (foreign key reference to UserProfile model).
        comment (str): The text of the comment.
        comment_image_path (str): The path to the image attached to the comment.
        date (str): The date when the comment was made.
    """
    product = models.ForeignKey(Product, models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    user_profile = models.ForeignKey(UserProfile, models.DO_NOTHING)
    comment = models.TextField(blank=True, null=True)
    comment_image_path = models.TextField(blank=True, null=True)
    date = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'comment'
    

class Shop(models.Model):
    """Represents a shop in the system.

    Attributes:
        user (User): The user associated with the shop (foreign key reference to User model).
        shop_name (str): The name of the shop.
        shop_phone (str): The phone number of the shop.
        shop_address (str): The address of the shop.
        shop_email (str): The email address of the shop.
        shop_type (str): The type or category of the shop.
        shop_description (str): The description of the shop.
        shop_image_path (str): The path to the image associated with the shop.
        paypal (str): The PayPal account linked to the shop.
    """
    user = models.ForeignKey(User, models.DO_NOTHING)
    shop_name = models.TextField(blank=True, null=True)
    shop_phone = models.TextField(blank=True, null=True)
    shop_address = models.TextField(blank=True, null=True)
    shop_email = models.TextField(blank=True, null=True)
    shop_type = models.TextField(blank=True, null=True) 
    shop_description = models.TextField(blank=True, null=True)
    shop_image_path = models.TextField(blank=True, null=True)
    paypal= models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shop'


class ShopDetail(models.Model):
    """Represents the details of a shop in the system.

    Attributes:
        user (User): The user associated with the shop (foreign key reference to User model).
        shop (Shop): The shop to which the details belong (foreign key reference to Shop model).
        product (Product): The product associated with the shop detail (foreign key reference to Product model).
    """
    user = models.ForeignKey(User, models.DO_NOTHING)
    shop = models.ForeignKey(Shop, models.DO_NOTHING)
    product = models.ForeignKey(Product, models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'shop_detail'


class Rating(models.Model):
    """Represents a rating given by a user to a product in the system.

    Attributes:
        user (User): The user who gave the rating (foreign key reference to User model).
        product (Product): The product being rated (foreign key reference to Product model).
        rating (int): The rating value given by the user.
        rate_time (datetime): The date and time when the rating was given.
    """
    user = models.ForeignKey(User, models.DO_NOTHING)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    rating = models.IntegerField(blank=True, null=True)
    rate_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rating'


class EcommerceCart(models.Model):
    """Represents a cart item in the ecommerce system.

    Attributes:
        quantity (int): The quantity of the product in the cart.
        created_at (datetime): The date and time when the cart item was created.
        product (Product): The product associated with the cart item (foreign key reference to Product model).
        price_ht (float): The price of the product without taxes.
        user (User): The user who owns the cart item (foreign key reference to User model).
        shop (Shop): The shop associated with the cart item (foreign key reference to Shop model).
    """
    quantity = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    product = models.ForeignKey(Product, models.DO_NOTHING)
    price_ht = models.FloatField(blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    shop = models.ForeignKey(Shop, models.DO_NOTHING)
    price_ttc = 0

    def price_tt(self):
        return self.quantity * self.product.product_price_new

    class Meta:
        managed = True
        db_table = 'ecommerce_cart'