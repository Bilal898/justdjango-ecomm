from django.shortcuts import render, get_object_or_404
from .models import Item, Order, OrderItem
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib import messages
# Create your views here.


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class HomeView(ListView):
    model = Item
    template_name = "home.html"


def add_to_cart(request, slug):
    print("req", request)
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item updated in cart")

        else:
            order.items.add(order_item)
            messages.info(request, "Item added to cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, "Item updated in cart")

    return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    print("slug", slug)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False)[0]
            order.items.remove(order_item)
            # order_item.delete()
            return redirect("core:product", slug=slug)
            messages.info(request, "Item removed from cart")

        else:
            messages.info(request, "Item not in cart")
            return redirect("core:product", slug=slug)

    else:
        messages.info(request, "No active order found")
        return redirect("core:product", slug=slug)
