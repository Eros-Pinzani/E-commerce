from django.shortcuts import redirect, render
from Carts.models import CartItem
from Store.models import Product
from .forms import OrderForm
from .models import Order, OrderProduct
import datetime

# Create your views here.
def update(request, order):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    CartItem.objects.filter(user=request.user).delete()
    return render(request, 'orders/order_complete.html')


def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (total * 22) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.is_ordered = True  # Imposta l'ordine come completato
            data.status = 'Completed'  # Imposta lo stato a Completed
            data.save()
            # Genera il numero ordine
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            # Salva i prodotti del carrello in OrderProduct
            update(request, data)
            return redirect('order_complete')
    else:
        return redirect('checkout')


def order_complete(request):
    # Recupera l'ultimo ordine effettuato dall'utente
    order = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at').first()
    if not order:
        return redirect('store')
    order_products = OrderProduct.objects.filter(order=order)
    context = {
        'order': order,
        'order_products': order_products,
        'total': order.order_total,
        'tax': order.tax,
        'grand_total': order.order_total,
    }
    return render(request, 'orders/order_complete.html', context)
