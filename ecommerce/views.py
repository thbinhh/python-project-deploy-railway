from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from ecommerce.models import *
from .models import Product, Category
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import TextInput, PasswordInput
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.contrib import messages
from django.urls import reverse
from django.db.models import Case, When
from django import forms
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
import json
import numpy as np
from scipy.spatial.distance import cosine
from django.contrib.auth import logout
from django.db.models import Q
from django.db.models import Sum
from django.core.paginator import Paginator


def user_based_collaborative_filtering(user_id):
    # Retrieve all users and items
    users = User.objects.exclude(id=user_id)
    products = Product.objects.all()
    # Create a matrix to store user-item ratings
    ratings_matrix = np.zeros((users.count() + 1, products.count()))

    # Iterate over users and items to populate the ratings matrix
    for i, u in enumerate(users):
        for j, product in enumerate(products):
            try:
                rating = Rating.objects.get(user=u, product=product)
                ratings_matrix[i, j] = rating.rating
            except Rating.DoesNotExist:
                continue
    # Calculate similarity between users
    user_similarities = np.zeros(users.count())

    for i in range(users.count()):
        user_similarities[i] = 1 - cosine(ratings_matrix[user_id-1], ratings_matrix[i])

    # Sort users by similarity
    sorted_users = np.argsort(-user_similarities)

    # Get top N similar users
    top_similar_users = sorted_users[:10]
    # Collect items rated by top similar users but not rated by the target user
    recommendations = set()
    for u in top_similar_users:
        for j, item in enumerate(products):
            if ratings_matrix[user_id-1, j] == 0 and ratings_matrix[u, j] > 0:
                recommendations.add(item)
    
    return recommendations


class HomeView(ListView):
    """Renders the home page with a list of categories and products.

    Attributes:
        model (Category): The model used for retrieving the categories.
        queryset (QuerySet): The queryset used for retrieving all categories.
        template_name (str): The name of the template used for rendering the home page.
    """
    model = Category
    queryset = Category.objects.all()
    template_name = 'home/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


def productdetail(request, product_id):
    """Renders the product detail page.

    Retrieves the product, related products, comments, and shop details from the database,
    and renders the product detail page with the retrieved data.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product to display.

    Returns:
        HttpResponse: The rendered product detail page.
    """
    product = get_object_or_404(Product, product_id=product_id)
    products = Product.objects.all()
    comments = Comment.objects.filter(product_id=product_id)
    rating_values = list(range(1, 6))

    comment_data = []
    for comment in comments:
        comment_data.append({
            'comment': comment.comment,
            'comment_image_path': comment.comment_image_path,
            'date': comment.date,
            'user_firstname': comment.user.first_name,
            'user_lastname': comment.user.last_name,
            'user_profile_image': comment.user_profile.user_image_path
        })

    shopdetail = ShopDetail.objects.get(product_id = product_id).shop_id
    print(shopdetail)
    shop = Shop.objects.get(id = shopdetail)
    if request.user.is_authenticated:
        try:
            rating_user = Rating.objects.get(user=request.user, product_id=product_id).rating
        except Rating.DoesNotExist:
            rating_user = 0
    else:
        rating_user = 0

    sell_quantity = OrderDetail.objects.filter(product_id=product_id, status='Hoàn thành').values('product_id').count()

    
    if request.user.is_authenticated:
        product_recommend = user_based_collaborative_filtering(request.user.id)
        return render(request, 'home/detail.html', {'product': product, 'products': products, 'comments': comment_data, 'shop': shop, 'rating_values' : rating_values, 'rating_user': rating_user, 'sell_quantity': sell_quantity, 'product_recommend': product_recommend})
    else:
        return render(request, 'home/detail.html', {'product': product, 'products': products, 'comments': comment_data, 'shop': shop, 'rating_values' : rating_values, 'rating_user': rating_user, 'sell_quantity': sell_quantity, 'product_recommend': products})



def shop(request, page):
    """
    Renders the shop page.

    Retrieves all categories, products, and shops from the database,
    paginates the products, and renders the shop page with the retrieved data.

    Args:
        request (HttpRequest): The HTTP request object.
        page (int): The page number of the product pagination.

    Returns:
        HttpResponse: The rendered shop page.
    """
    categories = Category.objects.all()
    products = Product.objects.all()
    shops = Shop.objects.all()
    products = Paginator(products, 12)
    page_number = page
    products = products.get_page(page_number)
    type = 'shop'
    return render(request, 'home/shop.html', {'categories': categories, 'products': products, 'shops': shops, 'type': type})


def shop_rating(request, page):
    """
    Renders the shop page sorted by rating.

    Retrieves all categories, products, and shops from the database,
    orders the products by rating in descending order,
    paginates the products, and renders the shop page with the retrieved data.

    Args:
        request (HttpRequest): The HTTP request object.
        page (int): The page number of the product pagination.

    Returns:
        HttpResponse: The rendered shop page sorted by rating.
    """
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-rate')
    shops = Shop.objects.all()
    products = Paginator(products, 12)
    page_number = page
    products = products.get_page(page_number)
    type = 'shop-rating'
    return render(request, 'home/shop.html', {'categories': categories, 'products': products, 'shops': shops, 'type': type})


def shop_popularity(request, page):
    """
    Renders the shop page sorted by popularity.

    Retrieves all categories, products, and shops from the database,
    filters the products based on completed orders,
    annotates the products with the total quantity sold,
    orders the products by total quantity in descending order,
    paginates the products, and renders the shop page with the retrieved data.

    Args:
        request (HttpRequest): The HTTP request object.
        page (int): The page number of the product pagination.

    Returns:
        HttpResponse: The rendered shop page sorted by popularity.
    """
    categories = Category.objects.all()
    products = Product.objects.filter(
    orderdetail__status='Hoàn thành'
    ).annotate(
        total_quantity=Sum('orderdetail__product_quantity')
    ).order_by('-total_quantity')
    shops = Shop.objects.all()
    products = Paginator(products, 12)
    page_number = page
    products = products.get_page(page_number)
    type = 'shop-popularity'
    return render(request, 'home/shop.html', {'categories': categories, 'products': products, 'shops': shops, 'type': type})


class MyForm(forms.Form):
    price = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    shop = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    ship = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    category = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)


def filter(request):
    """
    Filters and renders the shop page based on user-selected filters.

    Retrieves the form data from the request,
    extracts the selected price range, shipping options, shop IDs, and category IDs,
    defines dictionaries for price ranges and shipping options,
    retrieves all categories, shops, and products from the database,
    applies the selected filters to the products,
    and renders the shop page with the filtered products and other data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered shop page with the filtered products and other data.
    """
    form = MyForm(request.POST)
    price_range = request.POST.getlist('price')
    ship = form.data.getlist('ship')
    shop = form.data.getlist('shop')
    category = form.data.getlist('category')
    prices = {
        'price0': (0, 100000),
        'price1': (100000, 200000),
        'price2': (200000, 500000),
        'price3': (500000, 1000000),
        'price4': (1000000, 3000000),
        'price5': (3000000, 5000000),
    }

    ships = {
        'trongnuoc': 'Trong nước',
        'quocte': 'Quốc tế'
    }

    categories = Category.objects.all()
    shops = Shop.objects.all()
    products = Product.objects.all()

    if(len(price_range) != 0):
        selected_values = price_range
        selected_prices = [prices[value] for value in selected_values]
        min_price = min([price[0] for price in selected_prices])
        max_price = max([price[1] for price in selected_prices])
        products = products.filter(product_price_new__gte=min_price, product_price_new__lte=max_price)

    if(len(category) != 0):
        products = products.filter(cate_id_id__in=category)

    if(len(shop) != 0):
        shopfilter = shops.filter(id__in = shop)
        product_ids = ShopDetail.objects.filter(shop_id__in=shopfilter.values_list('id', flat=True)).values_list('product_id', flat=True)
        products = products.filter(product_id__in=product_ids)

    if(len(ship) != 0):
        selected_values = ship
        selected_ship = [ships[value] for value in selected_values]
        products = products.filter(type__in=selected_ship)

    return render(request, 'home/shop.html', {'categories': categories, 'products': products, 'shops': shops})


def login_view(request):
    """
    Handles the login functionality.

    If the request method is POST, retrieves the username and password from the form,
    authenticates the user using the provided credentials,
    if the authentication is successful, logs in the user and redirects to the home page,
    otherwise, displays an error message and renders the login/signup page with the error message.

    If the request method is GET, renders the login/signup page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered login/signup page or a redirect to the home page.
    """
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Display an error message
            error_message = 'Invalid username or password.'
            return render(request, 'home/login_signup.html', {'error_message': error_message})
    else:
        return render(request, 'home/login_signup.html')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
        else:
            error_message = form.errors
            print(error_message)
            render(request, 'home/login_signup.html', {'error_message': error_message})
    else:
        form = UserCreationForm()
    return render(request, 'home/login_signup.html', {'form': form})


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': TextInput(attrs={'placeholder': 'Enter your name', 'required': True}),
            'email': TextInput(attrs={'placeholder': 'Enter your email', 'required': True}),
            'password1': PasswordInput(attrs={'placeholder': 'Enter your password', 'required': True}),
            'password2': PasswordInput(attrs={'placeholder': 'Confirm your password', 'required': True}),
        }


class CustomUserLoginForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
            'username': TextInput(attrs={'placeholder': 'Enter your name', 'required': True}),
            'password': PasswordInput(attrs={'placeholder': 'Enter your password', 'required': True}),
        }


@login_required
def cart(request):
    """
    Renders the cart page and displays the items in the user's cart.

    The function first sets the 'cart_visited' flag in the session to True to indicate that the cart has been visited.
    It then retrieves the cart items for the logged-in user and orders them by the creation date.
    
    Calculates the total price of the cart by summing the individual item prices multiplied by their quantities.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered cart page with the cart items and total price.
    """
    request.session['cart_visited'] = True
    cart_items = EcommerceCart.objects.filter(user=request.user).order_by('created_at')
    
    total_price = sum(item.quantity * float(item.product.product_price_new) for item in cart_items)
    return render(request, 'home/cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def add_to_cart(request, product_id):
    """
    Adds a product to the user's cart.

    Retrieves the quantity and shop information from the request's POST data.
    Retrieves the shop object based on the provided shop ID.
    Attempts to get or create a cart item for the user, product, and shop combination.
    If the cart item already exists, the quantity is updated by adding the provided quantity.
    Finally, redirects the user to the cart page.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product to be added to the cart.

    Returns:
        HttpResponseRedirect: A redirect response to the cart page.
    """
    quantity = request.POST['quantity']
    shop_get = request.POST['shop_id']
    shop = Shop.objects.get(id = shop_get)
    cart_item, created = EcommerceCart.objects.get_or_create(user=request.user, product_id=product_id, quantity = quantity, shop = shop)
    if not created:
        cart_item.quantity += int(quantity)
        cart_item.save()
    return redirect('cart')

@login_required
def remove_from_cart(request, cart_item_id):
    """
    Removes a cart item from the user's cart.

    Retrieves the cart item object based on the provided cart item ID and user.
    Deletes the cart item.
    Finally, redirects the user to the cart page.

    Args:
        request (HttpRequest): The HTTP request object.
        cart_item_id (int): The ID of the cart item to be removed.

    Returns:
        HttpResponseRedirect: A redirect response to the cart page.
    """
    cart_item = get_object_or_404(EcommerceCart, pk=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout(request):
    """
    Handles the checkout process for the user's cart.

    If the request method is POST:
    - Retrieves the selected items from the form.
    - Validates the selected items and calculates the total price.
    - Validates and applies the coupon discount if provided.
    - Renders the checkout page with the cart items, total price, discount value, and coupon ID.

    If the request method is GET:
    - Renders the checkout page without any cart items.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The response containing the rendered checkout page.
    """
    if request.method == 'POST':
        selectedItems = request.POST.get('selectedItems')
        if(len(selectedItems)==0):
            error = ('Please choose one item in cart')
            messages.error(request, error)
            return redirect('cart')
        
        selected_items = json.loads(selectedItems)
        item_ids = [item['itemId'] for item in selected_items]

        selectedItems = selectedItems.split(',') if selectedItems else []
        cart_items = EcommerceCart.objects.filter(user=request.user, id__in=item_ids)
        total_price = sum(item.quantity * float(item.product.product_price_new) for item in cart_items)
        coupon_get = request.POST.get('coupon')
        coupon_id = 0
        if(len(coupon_get) != 0):
                discount = Coupon.objects.filter(coupon=coupon_get).values()
                if(discount):
                    coupon_id = discount.values()[0].get('id')
                    couponused = CouponUsed.objects.filter(coupon = coupon_id, user = request.user)
                    if(couponused.exists()):
                        error = ('Coupon is used')
                        messages.error(request, error)
                        return redirect('cart')
                    else:
                        discount_value = discount.values()[0].get('decrease')
                        total_price = total_price * (100 - discount_value) / 100
                    
                else:
                    error = ('Coupon does not exist')
                    messages.error(request, error)
                    return redirect('cart')
        else:
            discount_value = 0

        return render(request, 'home/checkout.html', {'cart_items': cart_items, 'total_price': total_price, 'discount': discount_value, 'couponid': coupon_id})
        
    return render(request, 'home/checkout.html')


@login_required
def checkout_paypal(request):
    """
    Handles the checkout process for PayPal payment.

    If the request method is POST:
    - Retrieves the selected items from the form.
    - Validates the selected items and checks if they belong to the same shop.
    - Calculates the total price and applies the coupon discount if provided.
    - Constructs the PayPal payment form.
    - Renders the checkout page with the cart items, total price, discount value, coupon ID, and PayPal form.

    If the request method is GET:
    - Renders the checkout page without any cart items.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The response containing the rendered checkout page with the PayPal payment form.
    """
    if request.method == 'POST':
        selectedItems = request.POST.get('selectedItems')
        if(len(selectedItems)==0):
            error = ('Please choose one item in cart')
            messages.error(request, error)
            return redirect('cart')
        
        selected_items = json.loads(selectedItems)
        second_values = [item['secondValue'] for item in selected_items]
        item_ids = [item['itemId'] for item in selected_items]

        if len(selected_items) != 1:
            is_different = len(set(second_values)) == len(selected_items)
            if is_different:
                    error = ('Nếu thanh toán bằng Paypal các sản phẩm phải cùng một shop.')
                    messages.error(request, error)
                    return redirect('cart')
        
        cart_items = EcommerceCart.objects.filter(user=request.user, id__in=item_ids)
        total_price = sum(item.quantity * float(item.product.product_price_new) for item in cart_items)
        coupon_get = request.POST.get('coupon')
        coupon_id = 0
        if(len(coupon_get) != 0):
                discount = Coupon.objects.filter(coupon=coupon_get).values()
                if(discount):
                    coupon_id = discount.values()[0].get('id')
                    couponused = CouponUsed.objects.filter(coupon = coupon_id, user = request.user)
                    if(couponused.exists()):
                        error = ('Coupon is used')
                        messages.error(request, error)
                        return redirect('cart')
                    else:
                        discount_value = discount.values()[0].get('decrease')
                        total_price = total_price * (100 - discount_value) / 100
                    
                else:
                    error = ('Coupon does not exist')
                    messages.error(request, error)
                    return redirect('cart')
        else:
            discount_value = 0
        paypal_address = second_values[0]
        print(paypal_address)
        paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': total_price,
        'notify_url': 'http://localhost:8000/checkout-paypal' + reverse('paypal-ipn'),
        'return_url': 'http://localhost:8000/checkout-paypal',
        'cancel_return': 'http://localhost:8000/payment-failed',
        }

        form_paypal = PayPalPaymentsForm(initial=paypal_dict)
        
        return render(request, 'home/checkout_paypal.html', {'cart_items': cart_items, 
                                                             'total_price': total_price, 
                                                             'discount': discount_value, 
                                                             'couponid': coupon_id, 
                                                             'paypal_address': paypal_address})
        
    return render(request, 'home/checkout.html')


@login_required
def checkout_paypal_success(request):
    """
    Handles the successful payment response from PayPal.

    Retrieves the form data from the cookies, including the cart IDs, coupon ID, email, phone, address, district, and province.
    Fetches the cart items based on the cart IDs.
    Calculates the total price with the applied coupon discount.
    Renders the checkout success page with the cart items, total price, discount value, coupon ID, email, phone, address, district, 
    and province.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The response containing the rendered checkout success page with the relevant information.
    """
    form_data = request.COOKIES.get('form_data')
    form_data = json.loads(form_data)

    cart_ids = form_data.get('cart_ids', [])
    coupon_id = int(form_data.get('coupon_id', '0'))
    email = form_data.get('email', '')
    phone = form_data.get('phone', '')
    diachi = form_data.get('diachi', '')
    huyen = form_data.get('huyen', '')
    tinh = form_data.get('tinh', '')

    cart_items = EcommerceCart.objects.filter(user=request.user, id__in=cart_ids)
    total_price = sum(item.quantity * float(item.product.product_price_new) for item in cart_items)
    total_price = total_price * (100 - coupon_id) / 100
    return render(request, 'home/checkout_paypal_success.html', {'cart_items': cart_items, 
                                                  'total_price': total_price, 
                                                  'discount': coupon_id, 
                                                  'couponid': coupon_id,
                                                  'email': email,
                                                  'phone': phone,
                                                  'diachi': diachi,
                                                  'huyen': huyen,
                                                  'tinh': tinh})



@login_required
def sendcheckout(request):
    """
    Processes the checkout request and creates an order.

    Retrieves the necessary data from the request, including quantities, product IDs, cart IDs, coupon ID, email, phone, address, 
    district, province, payment type, and status.
    Calculates the total price based on the quantities and product prices.
    Creates an order with the user, shipping information, order date, total price, status, email, address, and payment type.
    Retrieves the coupon based on the coupon ID.
    Creates order details for each product with the order, product, quantity, order detail date, status, and discount.
    If a coupon other than the default coupon is used, marks the coupon as used by the user.
    Deletes the cart items associated with the cart IDs.
    Redirects the user to the cart page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: The redirect response to the cart page.
    """
    if 'cart_visited' in request.session and request.session['cart_visited']:
            quantities = request.POST.getlist('quantities[]')
            product_ids = request.POST.getlist('product_id[]')
            cart_id = request.POST.getlist('cart_id[]')
            coupon_id_get = request.POST.get('couponid')
            email_get = request.POST.get('email')
            phone = request.POST.get('phone')
            diachi = request.POST.get('diachi')
            huyen = request.POST.get('huyen')
            tinh = request.POST.get('tinh')
            payment = request.POST.get('payment')
            status = request.POST.get('status')

            total_price_cal = 0

            for quantity, product_id in zip(quantities, product_ids):
                product_item = Product.objects.get(product_id=product_id)
                product_price = product_item.product_price_new
                item_total = int(quantity) * product_price
                total_price_cal += item_total


            order = Order.objects.create(
                user = request.user,
                ship_name=request.user.get_full_name(),
                ship_address=str(diachi + ' ' + huyen + ' ' + tinh),  
                ship_phone=phone,  
                order_date=timezone.now(),
                total_price = total_price_cal,
                order_status=status,  
                email = email_get,
                diachi = diachi,
                huyen = huyen,
                tinh = tinh,
                payment_type = payment
            )

            if(coupon_id_get == '0'):
                coupon = Coupon.objects.filter(id=1)[0]
            else:
                coupon = Coupon.objects.filter(id=coupon_id_get)[0]

            for product_id, quantity in zip(product_ids, quantities):
                OrderDetail.objects.create(
                    order_id = order,
                    product = Product.objects.filter(product_id=product_id)[0],
                    product_quantity=quantity,
                    order_detail_date=timezone.now(),
                    status = status,
                    discount = coupon
                )
            if(coupon.id != 1 ):
                CouponUsed.objects.create(
                    coupon_id = coupon.id,
                    user_id = request.user.id
                )

            EcommerceCart.objects.filter(id__in=cart_id).delete()
    return redirect('cart')
    


@login_required
def profile(request):
    """Renders the user profile page.

    Retrieves the authenticated user's information and profile details from the database,
    and renders the profile page with the user and user_profile data.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered profile page.
    """
    user_id = request.user.id
    user = AuthUser.objects.filter(id=user_id).values()[0]
    user_profile = UserProfile.objects.filter(user_id=user_id).values()[0]
    return render(request, 'home/profile.html', {'user': user, 'user_profile': user_profile})


@login_required
def update_profile(request):
    """
    Updates the user profile with the provided information.

    Retrieves the first name, last name, bio, age, address, phone, and host status from the request.
    Updates the first name and last name of the user.
    Retrieves the user profile associated with the user.
    Updates the bio, age, address, phone, and host fields of the user profile.
    Saves the user and user profile.
    Redirects the user to the profile page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: The redirect response to the profile page.
    """
    first_name = request.POST.get('firstname')
    last_name = request.POST.get('lastname')
    user = request.user
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    profile = get_object_or_404(UserProfile, user=user)
    profile.bio = request.POST.get('bio', '')
    profile.age = request.POST.get('age', None)
    profile.address = request.POST.get('address', '')
    profile.phone = request.POST.get('phone', '')
    profile.host = request.POST.get('host', False)
    # profile.user_image_path = request.POST.get('user_image_path', '')
    profile.save()
    return redirect('profile')


@login_required
def order(request):
    """
    Retrieves the orders placed by the logged-in user.

    Retrieves the orders associated with the logged-in user.
    Retrieves the order details for the retrieved orders.
    Orders are sorted in descending order based on the order detail date.
    Renders the 'order.html' template with the retrieved order items.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered 'order.html' template.
    """
    order = Order.objects.filter(user=request.user).values()
    order_ids = [item['order_id'] for item in order]
    order_items = OrderDetail.objects.filter(order_id__in=order_ids).order_by('-order_detail_date')
    return render(request, 'home/order.html', {'order_items':order_items})


@login_required
def contact(request):
    """
    Renders the 'contact.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response containing the rendered 'contact.html' template.
    """
    return render(request, 'home/contact.html')


@login_required
def addfavorite(request, product_id):
    """
    Adds or removes a product from the user's favorites list.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product.

    Returns:
        HttpResponse: The HTTP response redirecting to the 'favorite' page.
    """
    product = Product.objects.get(product_id = product_id)
    user = request.user
    favorite = Favorite.objects.filter(product_id = product_id, user_id = user.id)
    if(favorite.exists()):
        favorite.delete()
    else:
        Favorite.objects.create(
            product = product,
            user = user
        )
    return redirect('favorite')


@login_required
def favorite(request):
    """
    Displays the user's favorite products.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response rendering the 'favorite' page.
    """
    user = request.user
    favorite_list = Favorite.objects.filter(user_id = user.id)
    if favorite_list.exists():
        # If favorites exist, retrieve the products
        products = Product.objects.filter(product_id__in=favorite_list.values('product_id'))
        return render(request, 'home/favorite.html', {'products': products})
    else:
        # If no favorites exist, return a message
        message = "You don't have any favorites yet."
        return render(request, 'home/favorite.html', {'message': message})
    

@login_required
def addcomment(request, product_id):
    """
    Adds a comment to a product.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product to add the comment to.

    Returns:
        HttpResponse: A redirect to the 'home' page.
    """
    user = request.user
    product = Product.objects.get(product_id = product_id)
    user_profile = UserProfile.objects.get(user_id = user.id)
    comment_get = request.POST.get('comment')
    Comment.objects.create(
        product = product,
        user = user,
        user_profile = user_profile,
        comment = comment_get,
        date = date.today() 
    )
    return redirect('home')


@login_required
def becomehost(request):
    """
    Renders the 'becomehost' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'becomehost' template with user and user_profile context.
    """
    user_id = request.user.id
    user = AuthUser.objects.filter(id=user_id).values()[0]
    user_profile = UserProfile.objects.filter(user_id=user_id).values()[0]
    return render(request, 'home/becomehost.html', {'user': user, 'user_profile': user_profile})


@login_required
def addproduct(request):
    """
    Renders the 'addproduct' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered 'addproduct' template with user, user_profile, shop, and categories context.
    """
    user_id = request.user.id
    user = AuthUser.objects.filter(id=user_id).values()[0]
    user_profile = UserProfile.objects.filter(user_id=user_id).values()[0] 
    shop = Shop.objects.filter(user_id=user_id).values()[0]
    categories = Category.objects.all()
    return render(request, 'home/addproduct.html', {'user': user, 'user_profile': user_profile,'shop': shop, 'categories': categories})



@login_required
def createshop(request):
    """
    Creates a new shop for the logged-in user and redirects to the 'shopdetail' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'shopdetail' page.
    """
    user = request.user
    Shop.objects.create(
        user = user,
        shop_name = request.POST.get('name'),
        shop_email = request.POST.get('email'),
        shop_address = request.POST.get('address'),
        shop_phone = request.POST.get('phone'),
        shop_type = request.POST.get('type'),
        shop_description = request.POST.get('description')
    )
    return redirect('shopdetail')


@login_required
def createproduct(request):
    """
    Creates a new product for the logged-in user's shop and redirects to the 'shopdetail' page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the 'shopdetail' page.
    """
    user = request.user
    category = Category.objects.get(cate_id = request.POST.get('cate'))
    product = Product.objects.create(
        cate_id = category,
        product_name = request.POST.get('name'),
        product_price = request.POST.get('price'),
        product_price_new = request.POST.get('price'),
        product_quantity = request.POST.get('quantity'),
        product_detail = request.POST.get('name'),
        product_status = '1',
        description = request.POST.get('description'),
        information = request.POST.get('information'),
        image_path = models.TextField(blank=True, null=True)
    )
    ShopDetail.objects.create(
        user = user,
        product = product
    )
    return redirect('shopdetail')


@login_required
def shopdetail(request):
    """
    Retrieves the shop details for the logged-in user and renders the 'myshop' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'myshop' template with the shop items.
    """
    shop_items = ShopDetail.objects.filter(user=request.user)
    return render(request, 'home/myshop.html', {'shop_items': shop_items})


@login_required
def remove_from_shop(request, shop_detail_id):
    """
    Removes a shop item from the user's shop and redirects to the 'shopdetail' page.

    Args:
        request (HttpRequest): The HTTP request object.
        shop_detail_id (int): The ID of the shop item to be removed.

    Returns:
        HttpResponse: Redirects to the 'shopdetail' page.
    """
    item_item = get_object_or_404(ShopDetail, pk=shop_detail_id, user=request.user)
    item_item.delete()
    return redirect('shopdetail')


@login_required
def editproduct(request, product_id):
    """
    Displays the form to edit a product in the user's shop.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product to be edited.

    Returns:
        HttpResponse: The rendered edit product form template.
    """
    user = request.user
    try:
        product = ShopDetail.objects.get(user_id=user.id, product_id=product_id).product
    except ShopDetail.DoesNotExist:
        return redirect(reverse('shopdetail'))
    user_id = request.user.id
    user = AuthUser.objects.filter(id=user_id).values()[0]
    shop = Shop.objects.filter(user_id=user_id).values()[0]
    category = Category.objects.filter(cate_id=product.cate_id_id).values()[0]
    categories = Category.objects.all()
    return render(request, 'home/editproduct.html', {'user':user, 
                                                     'shop': shop ,
                                                     'product': product, 
                                                     'category': category, 
                                                     'categories': categories})


@login_required
def editproductsend(request):
    """
    Updates the edited product in the user's shop.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the edit product page.
    """
    product_id = request.POST.get('product_id')
    category = Category.objects.get(cate_id = request.POST.get('cate'))
    product = get_object_or_404(Product, product_id=product_id)
    product.cate_id = category
    product.product_name = request.POST.get('name')
    product.product_price = request.POST.get('price')
    product.product_price_new = request.POST.get('price_new')
    product.product_quantity = request.POST.get('quantity')
    product.product_detail = request.POST.get('name')
    product.description = request.POST.get('description')
    product.information = request.POST.get('information')
    # product.user_image_path = request.POST.get('user_image_path', '')

    product.save()
    return redirect('editproduct',product_id)


@login_required
def ordershop(request):
    """
    Displays the orders for the products in the user's shop.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered template with the order details.
    """
    productid = ShopDetail.objects.filter(user_id = request.user.id).values_list('product_id', flat=True)
    order_detail = OrderDetail.objects.filter(product_id__in=productid).order_by('-order_detail_date')
    return render(request, 'home/ordershop.html', {'order_detail': order_detail})


@login_required
def editordershop(request):
    """
    Updates the status of an order in the user's shop.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the 'ordershop' view.
    """
    status = request.POST.get('status')
    orderupdate = request.POST.get('orderupdate')
    orderdetail = OrderDetail.objects.get(order_detail_id = orderupdate)
    orderdetail.status = status
    orderdetail.save()
    return redirect(ordershop)


@csrf_exempt
def payment_process(request):
    # paypal_dict = {
    #     'business': settings.PAYPAL_RECEIVER_EMAIL,
    #     'amount': '10.00',
    #     'item_name': 'Item Name',
    #     'notify_url': 'http://localhost:8000' + reverse('paypal-ipn'),
    #     'return_url': 'http://localhost:8000/home',
    #     'cancel_return': 'http://localhost:8000/payment-failed',
    # }

    # form = PayPalPaymentsForm(initial=paypal_dict)
    # print(form)
    # context = {'form': form}
    return render(request, 'home/null.html')


def payment_complete(request):
    return render(request, 'home/null.html')


def payment_failed(request):
    return render(request, 'home/null.html')


@login_required
def rating(request, product_id, rating):
    """
    Handles user ratings for a product.

    Args:
        request (HttpRequest): The HTTP request object.
        product_id (int): The ID of the product being rated.
        rating (int): The rating value provided by the user.

    Returns:
        HttpResponse: A redirect response to the 'product_detail' view for the rated product.
    """
    user = request.user
    product = get_object_or_404(Product, pk=product_id)

    # Check if a rating already exists for the user and product
    existing_rating = Rating.objects.filter(user=user, product_id=product_id).first()

    if existing_rating:
        # Update the existing rating
        existing_rating.rating = rating
        existing_rating.rate_time = timezone.now()
        existing_rating.save()
    else:
        # Create a new rating
        new_rating = Rating(user=user, product=product, rating=rating, rate_time=timezone.now())
        new_rating.save()

    product.rate = product.calculate_average_rating()
    product.save()

    return redirect('product_detail', product_id=product_id)


def logout_view(request):
    """
    Logs out the user and redirects them to the home page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the home page.
    """
    logout(request)
    return redirect('home')


def search_results(request):
    """
    Performs a search based on the provided keyword and returns the matching products.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A response containing the search results.
    """
    keyword = request.GET.get('keyword')
    products = Product.objects.filter(Q(product_name__icontains=keyword) | Q(product_name__icontains=keyword.capitalize()))
    categories = Category.objects.all()
    shops = Shop.objects.all()
    return render(request, 'home/shop.html', {'categories': categories, 'products': products, 'shops': shops})


@login_required
def shop_profile(request):
    """
    Retrieves the shop profile for the currently logged-in user and renders the shopprofile.html template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A response containing the rendered template with the shop information.
    """
    user_id = request.user.id
    shop = Shop.objects.get(user_id=user_id)
    return render(request, 'home/shopprofile.html', {'shop': shop})


@login_required
def update_shop(request):
    """
    Updates the shop profile for the currently logged-in user with the provided information.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response to the shop profile page.
    """
    user = request.user
    shop_profile = get_object_or_404(Shop, user_id=user.id)
    shop_profile.shop_name = request.POST.get('name')
    shop_profile.shop_email = request.POST.get('email')
    shop_profile.shop_address = request.POST.get('address')
    shop_profile.shop_phone = request.POST.get('phone')
    shop_profile.paypal = request.POST.get('palpayaddress')
    shop_profile.shop_type = request.POST.get('type')
    shop_profile.shop_description = request.POST.get('description')
    shop_profile.save()
    return redirect('shop_profile')





    
