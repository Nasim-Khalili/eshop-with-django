from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Order, OrderItem, Cart, CartItem
from .forms import ProductForm


def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'shop/product_list.html', {'products': products, 'categories': categories})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'محصول با موفقیت اضافه شد.')
            return redirect('shop:product_list')
    else:
        form = ProductForm()
    return render(request, 'shop/add_product.html', {'form': form})


@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'shop/cart.html', {'items': items, 'total': total})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    messages.success(request, f"{product.name} به سبد خرید اضافه شد")
    return redirect('shop:product_detail', pk=product.id)


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('shop:view_cart')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('shop:view_cart')


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.cartitem_set.all()

    if not items:
        messages.warning(request, "سبد خرید شما خالی است.")
        return redirect('shop:product_list')

    total = sum(item.total_price() for item in items)

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total=total,
            is_paid=True
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        items.delete()

        messages.success(request, "پرداخت با موفقیت انجام شد. سفارش شما ثبت گردید.")
        return redirect('shop:order_detail', order.id)

    return render(request, 'shop/checkout.html', {'items': items, 'total': total})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})