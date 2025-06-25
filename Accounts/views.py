from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from Carts.models import Cart, CartItem
from Category.models import Category
from Orders.models import Order, OrderProduct
from .forms import RegistrationForm, UserForm, UserProfileForm, CategoryForm, ProductForm, VariationForm, StockUpdateForm, AddVariationTypesForm, RemoveVariationTypeForm
from Store.models import Product, Variation, VariationType
from django.utils.text import slugify
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from Carts.views import _cart_id
import requests
from django.db import IntegrityError


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name,
                                               last_name=last_name,
                                               email=email,
                                               username=username,
                                               password=password
                                               )
            user.phone_number = phone_number
            user.is_manager = form.cleaned_data.get('is_manager', False)
            user.save()

            # Create UserProfile
            profile = UserProfile()
            profile.user_id = user.id
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Thank you for registering with us. A verification email has been sent to your email address. Please verify your account.')
            return redirect('/accounts/login/?command=verification&email='+ email)
        else:
            if 'email' in form.errors:
                for error in form.errors['email']:
                    messages.error(request, error)
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'Logged in successfully')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = get_object_or_404(UserProfile, user=request.user)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request, 'Account with this email does not exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has expired!')
        return redirect('login')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        user = Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password changed successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Current password is incorrect')
                return redirect('change_password')
        else:
            messages.error(request, 'New password and confirm password do not match')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)

@login_required(login_url='login')
def manager_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    return render(request, 'accounts/manager_dashboard.html')

@login_required(login_url='login')
def manager_categories(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    categories = Category.objects.all().order_by('category_name')
    if request.method == 'POST':
        if 'add_category' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                category = form.save(commit=False)
                category.slug = slugify(category.category_name)
                category.save()
                messages.success(request, 'Category added successfully.')
                return redirect('manager_categories')
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            category = Category.objects.get(id=category_id)
            category.delete()
            messages.success(request, 'Category and all related products have been deleted.')
            return redirect('manager_categories')
    else:
        form = CategoryForm()
    context = {
        'categories': categories,
        'form': form,
    }
    return render(request, 'accounts/manager_categories.html', context)

@login_required(login_url='login')
def manager_products(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    products = Product.objects.all().order_by('product_name')
    if request.method == 'POST':
        if 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            variation_type_names_raw = request.POST.get('variation_type_names', '')
            variation_type_names = variation_type_names_raw.splitlines()
            if form.is_valid():
                product = form.save(commit=False)
                base_slug = slugify(product.product_name)
                counter = 0
                while True:
                    slug = base_slug if counter == 0 else f"{base_slug}-{counter}"
                    product.slug = slug
                    try:
                        product.save()
                        break
                    except IntegrityError:
                        counter += 1
                for vt_name in variation_type_names:
                    if vt_name.strip():
                        VariationType.objects.create(product=product, name=vt_name.strip())
                messages.success(request, 'Product and variation types added successfully.')
                return redirect('manager_products')
        elif 'delete_product' in request.POST:
            form = ProductForm()
            product_id = request.POST.get('product_id')
            product = Product.objects.get(id=product_id)
            product.delete()
            messages.success(request, 'Product deleted successfully.')
            return redirect('manager_products')
        else:
            form = ProductForm()
    else:
        form = ProductForm()
    context = {
        'products': products,
        'form': form,
    }
    return render(request, 'accounts/manager_products.html', context)

@login_required(login_url='login')
def manager_variations(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    variations = Variation.objects.select_related('product', 'variation_category').all().order_by('product__product_name')
    if request.method == 'POST':
        product_id = request.POST.get('product')
        form = VariationForm(request.POST, product_id=product_id)
        if 'add_variation' in request.POST and form.is_valid():
            form.save()
            messages.success(request, 'Variation added successfully.')
            return redirect('manager_variations')
        elif 'delete_variation' in request.POST:
            variation_id = request.POST.get('variation_id')
            variation = Variation.objects.get(id=variation_id)
            variation.delete()
            messages.success(request, 'Variation deleted successfully.')
            return redirect('manager_variations')
    else:
        form = VariationForm()
    context = {
        'variations': variations,
        'form': form,
    }
    return render(request, 'accounts/manager_variations.html', context)

@login_required(login_url='login')
def manager_stock(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    products = Product.objects.all().order_by('product_name')
    if request.method == 'POST':
        form = StockUpdateForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            product.stock += quantity
            product.save()
            messages.success(request, f"Stock updated for {product.product_name} (+{quantity}).")
            return redirect('manager_stock')
    else:
        form = StockUpdateForm()
    context = {
        'products': products,
        'form': form,
    }
    return render(request, 'accounts/manager_stock.html', context)

@login_required(login_url='login')
def add_variation_types(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AddVariationTypesForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            variation_type_names = form.cleaned_data['variation_type_names'].splitlines()
            count = 0
            for vt_name in variation_type_names:
                vt_name = vt_name.strip()
                if vt_name:
                    VariationType.objects.create(product=product, name=vt_name)
                    count += 1
            messages.success(request, f'{count} variation types added to the product.')
            return redirect('manager_variations')
    else:
        form = AddVariationTypesForm()
    return render(request, 'accounts/add_variation_types.html', {'form': form})

@login_required(login_url='login')
def get_variation_types_for_product(request):
    product_id = request.GET.get('product_id')
    if product_id:
        variation_types = VariationType.objects.filter(product_id=product_id)
        data = [{'id': vt.id, 'name': vt.name} for vt in variation_types]
    else:
        data = []
    return JsonResponse({'variation_types': data})

@login_required(login_url='login')
def remove_variation_types(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    product_id = request.POST.get('product') if request.method == 'POST' else None
    form = RemoveVariationTypeForm(request.POST or None, product_id=product_id)
    if request.method == 'POST' and 'remove_variation_type' in request.POST:
        if form.is_valid():
            variation_type = form.cleaned_data['variation_type']
            Variation.objects.filter(variation_category=variation_type).delete()
            variation_type.delete()
            messages.success(request, 'Variation type and all associated variations have been deleted.')
            return redirect('remove_variation_types')
    return render(request, 'accounts/remove_variation_types.html', {'form': form})
