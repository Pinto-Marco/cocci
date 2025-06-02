from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from django.shortcuts import render, redirect
from product.models import Product, ProductImage
from .models import CartItem, Order, OrderItem

# Utility function to get or create a cart session ID
def get_or_create_cart_id(request):
    if 'cart_id' not in request.session or request.session['cart_id'] is None:
        request.session['cart_id'] = request.session.session_key or request.session.create()
    return request.session['cart_id']

class CartView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        responses={200: "Cart contents retrieved successfully"},
        description="Get the current cart contents"
    )
    def get(self, request):
        session_id = get_or_create_cart_id(request)
        cart_items = CartItem.objects.filter(session_id=session_id)
        
        # Calculate cart totals
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.total_price for item in cart_items)
        
        # Prepare cart items data
        items = []
        for item in cart_items:
            product_data = {
                'id': item.product.id,
                'code': item.product.code,
                'title': item.product.title,
                'price': item.product.price,
                'quantity': item.quantity,
                'total': item.total_price
            }
            items.append(product_data)
        
        cart_data = {
            'items': items,
            'total_items': total_items,
            'total_price': total_price
        }
        
        return Response(cart_data, status=status.HTTP_200_OK)

class AddToCartView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request={"type": "object", "properties": {
            "product_code": {"type": "string"},
            "quantity": {"type": "integer", "default": 1}
        }},
        responses={200: "Product added to cart", 404: "Product not found"},
        description="Add a product to the cart"
    )
    def post(self, request):
        if request.data:
            product_code = request.data.get('product_code')
            quantity = int(request.data.get('quantity', 1))
            is_api_call = True
        elif request.POST:
            product_code = request.POST.get('product_code')
            quantity = int(request.POST.get('quantity', 1))
            is_api_call = False
        else:
            return Response({"error": "Missing product_code or quantity"}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            product = Product.objects.get(code=product_code)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        session_id = get_or_create_cart_id(request)

        print("Session ID:", session_id)
        
        # Check if product already in cart
        CartItem.objects.get_or_create(
            product=product,
            session_id=session_id,
        )
        
        if is_api_call:
            return Response({"message": "Product added to cart"}, status=status.HTTP_200_OK)
        else:
            # Assuming you have a URL name 'product_detail' that takes 'product_code'
            return redirect('product_detail', product_code=product_code)

class RemoveFromCartView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request={"type": "object", "properties": {
            "product_code": {"type": "string"},
            "quantity": {"type": "integer", "default": 1},
            "remove_all": {"type": "boolean", "default": False}
        }},
        responses={200: "Product removed from cart", 404: "Product not found in cart"},
        description="Remove a product from the cart"
    )
    def post(self, request):
        product_code = request.data.get('product_code')
        session_id = get_or_create_cart_id(request)
        print("Session ID:", session_id)
        print("Product Code:", product_code)
        
        try:
            product = Product.objects.get(code=product_code)
            print("Product:", product)
            cart_item = CartItem.objects.get(product=product, session_id=session_id)
        except (Product.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Product not found in cart"}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item.delete()
        
        return Response({"message": "Product removed from cart"}, status=status.HTTP_200_OK)

class CheckoutView(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request={"type": "object", "properties": {
            "email": {"type": "string", "format": "email"}
        }},
        responses={200: "Order placed successfully", 400: "Invalid data or empty cart"},
        description="Complete the order with customer email"
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        session_id = get_or_create_cart_id(request)
        cart_items = CartItem.objects.filter(session_id=session_id)
        
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate total
        total = sum(item.total_price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            email=email,
            session_id=session_id,
            total=total
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
            )
        
        # Clear cart
        cart_items.delete()
        
        return Response({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total": order.total
        }, status=status.HTTP_200_OK)

def CartPageView(request):
    session_id = get_or_create_cart_id(request)
    cart_items = CartItem.objects.filter(session_id=session_id)
    
    # Calculate cart totals
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.total_price for item in cart_items)
    
    # Prepare cart items data
    items = []
    for item in cart_items:
        images = ProductImage.objects.filter(product=item.product)
        product_data = {
            'id': item.product.id,
            'code': item.product.code,
            'title': item.product.title,
            'price': item.product.price,
            'penalty': item.product.penalty,
            'quantity': item.quantity,
            'total': item.total_price,
            'image': images.first().image.url if images.exists() else None
        }
        items.append(product_data)
    
    context = {
        'cart_items': items,
        'total_items': total_items,
        'total_price': total_price
    }
    
    return render(request, 'cart.html', context)

def CheckoutPageView(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return redirect('cart')
        
        session_id = get_or_create_cart_id(request)
        cart_items = CartItem.objects.filter(session_id=session_id)
        
        if not cart_items.exists():
            return redirect('summary')
        
        # Calculate total
        total = sum(item.total_price for item in cart_items)
        
        # Create order
        order = Order.objects.create(
            email=email,
            session_id=session_id,
            total=total
        )
        
        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
            )
        
        # Clear cart
        cart_items.delete()
        
        return render(request, 'order_confirmation.html', {'order': order})
    
    session_id = get_or_create_cart_id(request)
    cart_items = CartItem.objects.filter(session_id=session_id)
    
    if not cart_items.exists():
        return redirect('cart')
    
    # Calculate cart totals
    total_items = sum(item.quantity for item in cart_items)
    total_price = sum(item.total_price for item in cart_items)
    
    context = {
        'total_items': total_items,
        'total_price': total_price
    }
    
    return render(request, 'checkout.html', context)


def ProductDetailView(request, code):
    product = Product.objects.get(code=code)
    images = ProductImage.objects.filter(product=product)
    context = {
        'product': product,
        'images': [image.image.url for image in images]
    }
    return render(request, 'product_detail.html', context)