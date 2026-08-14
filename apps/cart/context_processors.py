from apps.cart.models import Cart

def cart_context(request):
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if session_key:
            cart = Cart.objects.filter(session_key=session_key).first()

    return {
        'cart': cart,
        'cart_item_count': cart.total_items if cart else 0
    }
