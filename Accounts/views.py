from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.forms import modelform_factory
from django.views.decorators.http import require_GET

from Carts.models import Cart, CartItem
from Category.models import Category
from Orders.models import Order, OrderProduct
from Category.forms import CategoryForm
from Store.forms import ProductForm, VariationForm
from Accounts.forms import StockUpdateForm
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
from .forms import RegistrationForm, UserForm, UserProfileForm


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
        elif 'save_modify_category' in request.POST:
            cat_id = request.POST.get('modify_category_id')
            new_name = request.POST.get('modify_category_name')
            if cat_id and new_name:
                category = get_object_or_404(Category, id=cat_id)
                category.category_name = new_name
                category.slug = slugify(new_name)
                category.save()
                messages.success(request, 'Category updated successfully.')
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
        if 'add_product' in request.POST or 'add_product_and_variations' in request.POST:
            form = ProductForm(request.POST, request.FILES)
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
                messages.success(request, 'Product added successfully.')
                if 'add_product_and_variations' in request.POST:
                    return redirect(reverse('manager_variations') + f'?product_id={product.id}')
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
    products = Product.objects.all().order_by('product_name')
    variation_types = VariationType.objects.all().select_related('product')
    variation_values = Variation.objects.all().select_related('variation_category', 'product')
    form = VariationForm()

    if request.method == 'POST':

        if request.POST.get('variation_name') and request.POST.get('product_id'):
            # Aggiunta nuova variation type e valori
            product_id = request.POST.get('product_id')
            variation_name = request.POST.get('variation_name')
            values_str = request.POST.get('variation_values', '')
            values = [v.strip() for v in values_str.split(',') if v.strip()]
            # Se l'utente ha scritto un valore ma non ha cliccato su "Aggiungi", aggiungilo ora
            value_input = request.POST.get('variation_value_input', '').strip()
            if value_input:
                values.append(value_input)
            try:
                product = Product.objects.get(id=product_id)
                # Controllo unicità nome variazione per prodotto
                if VariationType.objects.filter(product=product, name__iexact=variation_name).exists():
                    messages.error(request, 'A variation with this name already exists for this product.')
                else:
                    vtype = VariationType.objects.create(product=product, name=variation_name)
                    for val in values:
                        Variation.objects.create(product=product, variation_category=vtype, variation_value=val)
                    messages.success(request, 'Variation and values added successfully.')
                    return redirect('manager_variations')
            except Product.DoesNotExist:
                messages.error(request, 'Product not found.')

            return render(request, 'accounts/manager_variations.html')
        elif 'delete_variation_value_id' in request.POST:
            value_id = request.POST.get('delete_variation_value_id')
            try:
                value = Variation.objects.get(id=value_id)
                value.delete()
                messages.success(request, 'Variation value deleted successfully.')
                return redirect('manager_variations')
            except Variation.DoesNotExist:
                messages.error(request, 'Variation value not found.')
        elif 'delete_variation_type_id' in request.POST:
            type_id = request.POST.get('delete_variation_type_id')
            try:
                vtype = VariationType.objects.get(id=type_id)
                Variation.objects.filter(variation_category=vtype).delete()
                vtype.delete()
                messages.success(request, 'Variation type and all its values deleted successfully.')
                return redirect('manager_variations')
            except VariationType.DoesNotExist:
                messages.error(request, 'Variation type not found.')
        # --- GESTIONE MODIFICA VARIAZIONE ---
        elif request.POST.get('modify_variation_type_id') and request.POST.get('modify_variation_name'):
            type_id = request.POST.get('modify_variation_type_id')
            new_name = request.POST.get('modify_variation_name')
            values_json = request.POST.get('modify_variation_values')
            import json
            try:
                data = json.loads(values_json)
                # Filtra i valori vuoti
                new_values = [v for v in data.get('values', []) if v.strip()]
                value_ids = data.get('ids', [])
            except Exception as e:
                new_values = []
                value_ids = []
            try:
                vtype = VariationType.objects.get(id=type_id)
                vtype.name = new_name
                vtype.save()
                # Aggiorna valori esistenti e aggiungi nuovi
                for idx, val in enumerate(new_values):
                    val_id = value_ids[idx] if idx < len(value_ids) else None
                    if val_id and str(val_id).isdigit():
                        try:
                            v = Variation.objects.get(id=val_id, variation_category=vtype)
                            v.variation_value = val
                            v.save()
                        except Variation.DoesNotExist:
                            pass
                    else:
                        # Nuovo valore (id None, null, vuoto, non numerico)
                        if not Variation.objects.filter(product=vtype.product, variation_category=vtype, variation_value=val).exists():
                            v=Variation.objects.create(product=vtype.product, variation_category=vtype, variation_value=val)
                            v.save()

                return redirect('manager_variations')
            except VariationType.DoesNotExist:
                messages.error(request, 'Variation type not found.')
    context = {
        'form': form,
        'products': products,
        'variation_types': variation_types,
        'variation_values': variation_values,
        'selected_product_id': None,
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
def product_edit(request, product_id):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    product = get_object_or_404(Product, id=product_id)
    variation_types = VariationType.objects.filter(product=product)
    if request.method == 'POST':
        form = None
        # Modifica prodotto
        if 'modify_product' in request.POST:
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product updated successfully.')
                return redirect('manager_products')
        # Modifica nome variation type
        elif 'edit_variation_type' in request.POST:
            vt_id = request.POST.get('variation_type_id')
            new_name = request.POST.get('variation_type_name')
            vt = get_object_or_404(VariationType, id=vt_id, product=product)
            vt.name = new_name
            vt.save()
            messages.success(request, 'Variation type updated successfully.')
            return redirect('product_edit', product_id=product.id)
        # Elimina variation type
        elif 'delete_variation_type' in request.POST:
            vt_id = request.POST.get('variation_type_id')
            vt = get_object_or_404(VariationType, id=vt_id, product=product)
            vt.delete()
            messages.success(request, 'Variation type deleted successfully.')
            return redirect('product_edit', product_id=product.id)
        # Se non è nessuno dei precedenti, oppure il form non è valido, assicura che form sia valorizzato
        if form is None:
            form = ProductForm(instance=product)
    else:
        form = ProductForm(instance=product)
    context = {
        'form': form,
        'product': product,
        'edit_mode': True,
        'variation_types': variation_types,
    }
    return render(request, 'accounts/product_edit.html', context)

@login_required(login_url='login')
def variation_list(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    variations = Variation.objects.select_related('product', 'variation_category').all().order_by('product__product_name')
    context = {
        'variations': variations,
    }
    return render(request, 'accounts/variation_list.html', context)

@login_required(login_url='login')
def variation_create(request):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    VariationFormDynamic = modelform_factory(Variation, exclude=[])
    if request.method == 'POST':
        form = VariationFormDynamic(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variazione creata con successo.')
            return redirect('variation_list')
    else:
        form = VariationFormDynamic()
    context = {
        'form': form,
    }
    return render(request, 'accounts/variation_form.html', context)

@login_required(login_url='login')
def variation_edit(request, variation_id):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    variation = get_object_or_404(Variation, id=variation_id)
    VariationFormDynamic = modelform_factory(Variation, exclude=[])
    if request.method == 'POST':
        form = VariationFormDynamic(request.POST, instance=variation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variazione aggiornata con successo.')
            return redirect('variation_list')
    else:
        form = VariationFormDynamic(instance=variation)
    context = {
        'form': form,
        'variation': variation,
    }
    return render(request, 'accounts/variation_form.html', context)

@login_required(login_url='login')
def variation_delete(request, variation_id):
    if not request.user.is_authenticated or not request.user.is_manager:
        return redirect('dashboard')
    variation = get_object_or_404(Variation, id=variation_id)
    if request.method == 'POST':
        variation.delete()
        messages.success(request, 'Variazione eliminata con successo.')
        return redirect('variation_list')
    context = {
        'variation': variation,
    }
    return render(request, 'accounts/variation_confirm_delete.html', context)

@require_GET
@login_required(login_url='login')
def get_variation_types_for_product(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({'error': 'Missing product_id'}, status=400)
    variation_types = VariationType.objects.filter(product_id=product_id)
    data = [
        {'id': vt.id, 'name': vt.name}
        for vt in variation_types
    ]
    return JsonResponse({'variation_types': data})
