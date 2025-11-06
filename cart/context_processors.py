from django.db.models import Sum
from .models import Cart


def cart_context(request):
    """Add cart count to all templates"""
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.get('cart_session_key')
            cart = Cart.objects.filter(session_key=session_key).first() if session_key else None
        
        if cart:
            cart_count = cart.items.aggregate(total=Sum('quantity'))['total'] or 0
        else:
            cart_count = 0
            
        return {'cart_count': cart_count}
    except:
        return {'cart_count': 0}
