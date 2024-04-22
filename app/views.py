from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .serelaizer import *
from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy('login')

def home(request):
    return render(request, 'home.html', context={})

@permission_classes([IsAuthenticated])
def shop(request):
    products = Product.objects.all()   
    return render(request, 'shop.html', {'products': products})

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 100.00:
            discount = 0.10  # 10% discount
        else:
            discount = 0
    
        discounted_price = product.price * (1 - discount)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        return redirect('cart')
    return render(request, 'product_detail.html', {'product': product})

# @api_view(['POST'])
def cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.subtotal() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@api_view(['DELETE'])
def delete_cart_item(request, cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def checkout(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.subtotal() for item in cart_items)
    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_price=total_price)
        order.items.set(cart_items)
        order.save()
        cart_items.delete()  # Clear the cart
        return redirect('order_success')
    return render(request, 'checkout.html', {'total_price': total_price})

def order_success(request):
    return render(request, 'order_success.html')

def detail(request):
    return render(request, 'details.html', context={})

def compare(request):
    return render(request, 'compare.html', context={})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def accounts(request):
    return render(request, 'accounts.html', context={})



