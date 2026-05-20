from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib import messages as django_messages
from django.contrib.auth.models import User
from .forms import WasteForm, ReviewForm, MessageForm, WasteFilterForm, BidForm
from .models import Waste, WishlistItem, Review, Message, Transaction, Bid
from .ml_pricing import predict_price


# Home page – latest listings
def home(request):
    latest_wastes = Waste.objects.filter(
        status='available'
    ).order_by('-created_at')[:6]
    
    waste_count = Waste.objects.filter(status='available').count()
    user_count = 100  # You can update this with actual count
    transactions = Transaction.objects.filter(status='completed').count()

    context = {
        'latest_wastes': latest_wastes,
        'waste_count': waste_count,
        'user_count': user_count,
        'transactions': transactions
    }
    return render(request, 'index.html', context)


# Waste detail page
def waste_detail(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    waste.views += 1
    waste.save()
    
    reviews = waste.reviews.all()
    average_rating = waste.get_average_rating()
    wishlist_item = None
    
    if request.user.is_authenticated:
        wishlist_item = WishlistItem.objects.filter(user=request.user, waste=waste).exists()
    
    bid_form = BidForm()
    bids = waste.bids.filter(status='pending').select_related('bidder')
    highest_bid = waste.bids.filter(status='pending').order_by('-amount').first()

    context = {
        'waste': waste,
        'reviews': reviews,
        'average_rating': average_rating,
        'is_wishlisted': wishlist_item,
        'is_seller': waste.user == request.user,
        'bids': bids,
        'highest_bid': highest_bid,
        'bid_form': bid_form
    }
    return render(request, 'marketplace/waste_detail.html', context)


# Upload waste + ML price prediction
@login_required
def upload_waste(request):
    if request.method == 'POST':
        form = WasteForm(request.POST, request.FILES)

        if form.is_valid():
            waste = form.save(commit=False)
            waste.user = request.user

            # 🔥 ML PRICE PREDICTION
            waste.predicted_price = predict_price(
                waste.waste_type,
                waste.weight_kg
            )

            # Initially final price = predicted price
            waste.final_price = waste.predicted_price

            waste.save()
            django_messages.success(request, 'Waste item uploaded successfully!')
            return redirect('my_listings')

    else:
        form = WasteForm()

    return render(
        request,
        'marketplace/upload_waste.html',
        {'form': form}
    )


# Enhanced marketplace with search and filter
def marketplace(request):
    wastes = Waste.objects.filter(status='available').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        wastes = wastes.filter(
            Q(description__icontains=search_query) |
            Q(waste_type__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Filter by waste type
    waste_type = request.GET.get('waste_type', '')
    if waste_type:
        wastes = wastes.filter(waste_type=waste_type)
    
    # Filter by price
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    if price_min:
        wastes = wastes.filter(final_price__gte=float(price_min))
    if price_max:
        wastes = wastes.filter(final_price__lte=float(price_max))
    
    # Sort
    sort_by = request.GET.get('sort_by', '-created_at')
    wastes = wastes.order_by(sort_by)
    
    filter_form = WasteFilterForm(request.GET)
    
    context = {
        'wastes': wastes,
        'filter_form': filter_form,
        'search_query': search_query,
    }
    return render(request, 'marketplace/marketplace.html', context)


# User's own listings
@login_required
def my_listings(request):
    wastes = Waste.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'marketplace/my_listings.html',
        {'wastes': wastes}
    )


# Edit waste listing
@login_required
def edit_waste(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    
    if waste.user != request.user:
        return HttpResponseForbidden("You can't edit this waste item.")
    
    if request.method == 'POST':
        form = WasteForm(request.POST, request.FILES, instance=waste)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Waste item updated successfully!')
            return redirect('my_listings')
    else:
        form = WasteForm(instance=waste)
    
    return render(request, 'marketplace/edit_waste.html', {'form': form, 'waste': waste})


# Delete waste listing
@login_required
def delete_waste(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    
    if waste.user != request.user:
        return HttpResponseForbidden("You can't delete this waste item.")
    
    if request.method == 'POST':
        waste.delete()
        django_messages.success(request, 'Waste item deleted successfully!')
        return redirect('my_listings')
    
    return render(request, 'marketplace/delete_waste.html', {'waste': waste})


# Add to wishlist
@login_required
def add_to_wishlist(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        waste=waste
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Added to wishlist'})
    
    return redirect('waste_detail', waste_id=waste_id)


# Remove from wishlist
@login_required
def remove_from_wishlist(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    WishlistItem.objects.filter(user=request.user, waste=waste).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Removed from wishlist'})
    
    return redirect('waste_detail', waste_id=waste_id)


# View wishlist
@login_required
def wishlist(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('waste')
    wastes = [item.waste for item in wishlist_items]
    
    return render(request, 'marketplace/wishlist.html', {'wastes': wastes})


# Add review to waste item
@login_required
def add_review(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    
    if waste.user == request.user:
        django_messages.error(request, "You can't review your own item.")
        return redirect('waste_detail', waste_id=waste_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.waste = waste
            review.reviewer = request.user
            review.save()
            django_messages.success(request, 'Review added successfully!')
            return redirect('waste_detail', waste_id=waste_id)
    else:
        form = ReviewForm()
    
    return render(request, 'marketplace/add_review.html', {'form': form, 'waste': waste})


# Send message
@login_required
def send_message(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = waste.user
            message.waste = waste
            message.save()
            django_messages.success(request, 'Message sent successfully!')
            return redirect('waste_detail', waste_id=waste_id)
    else:
        form = MessageForm()
    
    return render(request, 'marketplace/send_message.html', {'form': form, 'waste': waste})


# Inbox
@login_required
def inbox(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = messages.filter(is_read=False).count()
    
    return render(request, 'marketplace/inbox.html', {
        'messages': messages,
        'unread_count': unread_count
    })


# User profile
def user_profile(request, user_id):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, id=user_id)
    wastes = Waste.objects.filter(user=user, status='available')
    reviews = Review.objects.filter(waste__user=user)
    average_rating = reviews.aggregate(rating_avg=__import__('django.db.models', fromlist=['Avg']).Avg('rating'))['rating_avg'] or 0
    
    context = {
        'profile_user': user,
        'wastes': wastes,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_sales': Waste.objects.filter(user=user, status='sold').count()
    }
    return render(request, 'marketplace/user_profile.html', context)


@login_required
def request_purchase(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id, status='available')
    if waste.user == request.user:
        django_messages.error(request, "You can't request your own item.")
        return redirect('waste_detail', waste_id=waste_id)

    transaction, created = Transaction.objects.get_or_create(
        waste=waste,
        buyer=request.user,
        seller=waste.user,
        defaults={
            'amount': waste.final_price or waste.predicted_price or 0,
            'status': 'pending'
        }
    )

    if not created and transaction.status == 'pending':
        django_messages.info(request, 'You already requested to purchase this item. Seller will respond soon.')
    elif transaction.status != 'pending':
        django_messages.warning(request, 'This item is already in progress or sold.')
    else:
        django_messages.success(request, 'Purchase request sent to the seller.')

    return redirect('waste_detail', waste_id=waste_id)


@login_required
def mark_sold(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id, user=request.user)
    if waste.status != 'available':
        django_messages.error(request, 'This item cannot be marked as sold.')
        return redirect('dashboard')

    waste.status = 'sold'
    waste.save()

    Transaction.objects.filter(waste=waste, status='pending').update(
        status='completed',
        completed_at=timezone.now()
    )

    django_messages.success(request, 'Listing marked as sold and related requests completed.')
    return redirect('dashboard')


@login_required
def place_bid(request, waste_id):
    waste = get_object_or_404(Waste, id=waste_id, status='available')
    if waste.user == request.user:
        django_messages.error(request, "You can't bid on your own item.")
        return redirect('waste_detail', waste_id=waste_id)

    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            Bid.objects.create(
                waste=waste,
                bidder=request.user,
                amount=amount,
                status='pending'
            )
            django_messages.success(request, 'Your bid has been submitted. Sellers will review it soon.')
        else:
            django_messages.error(request, 'Enter a valid bid amount.')

    return redirect('waste_detail', waste_id=waste_id)


@login_required
def accept_bid(request, waste_id, bid_id):
    waste = get_object_or_404(Waste, id=waste_id, user=request.user)
    bid = get_object_or_404(Bid, id=bid_id, waste=waste)

    if waste.status != 'available':
        django_messages.error(request, 'This listing is no longer available.')
        return redirect('waste_detail', waste_id=waste_id)

    bid.status = 'accepted'
    bid.save()
    waste.status = 'sold'
    waste.final_price = bid.amount
    waste.save()

    Transaction.objects.create(
        waste=waste,
        buyer=bid.bidder,
        seller=request.user,
        amount=bid.amount,
        status='completed',
        completed_at=timezone.now()
    )

    Bid.objects.filter(waste=waste).exclude(id=bid.id).update(status='rejected')
    django_messages.success(request, 'Bid accepted and sale completed.')
    return redirect('dashboard')


def nearby(request):
    location_query = request.GET.get('location', '')
    near_listings = Waste.objects.filter(status='available')

    if location_query:
        near_listings = near_listings.filter(location__icontains=location_query)
    else:
        near_listings = near_listings.order_by('-created_at')[:10]

    locations = Waste.objects.filter(status='available').values('location').annotate(count=Count('id')).order_by('-count')[:5]

    return render(request, 'marketplace/nearby.html', {
        'near_listings': near_listings,
        'location_query': location_query,
        'locations': locations,
    })


@login_required
def transactions(request):
    transactions = Transaction.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).select_related('waste', 'buyer', 'seller').order_by('-created_at')

    return render(request, 'marketplace/transactions.html', {'transactions': transactions})


# Dashboard
@login_required
def dashboard(request):
    user_wastes = Waste.objects.filter(user=request.user)
    sold_items = user_wastes.filter(status='sold').count()
    active_items = user_wastes.filter(status='available').count()
    total_revenue = sum([w.final_price for w in user_wastes.filter(status='sold') if w.final_price])
    
    recent_reviews = Review.objects.filter(waste__user=request.user).order_by('-created_at')[:5]
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    pending_requests = Transaction.objects.filter(seller=request.user, status='pending').count()
    completed_transactions = Transaction.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user),
        status='completed'
    ).count()
    recent_transactions = Transaction.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user)
    ).order_by('-created_at')[:5]

    bid_requests = Bid.objects.filter(waste__user=request.user, status='pending').count()
    top_categories = Waste.objects.filter(status='available').values('category').annotate(count=Count('id')).order_by('-count')[:5]
    chart_data = {
        'categories': [item['category'] for item in top_categories],
        'counts': [item['count'] for item in top_categories]
    }

    context = {
        'sold_items': sold_items,
        'active_items': active_items,
        'total_revenue': total_revenue,
        'recent_reviews': recent_reviews,
        'unread_messages': unread_messages,
        'pending_requests': pending_requests,
        'completed_transactions': completed_transactions,
        'recent_transactions': recent_transactions,
        'user_wastes': user_wastes.order_by('-created_at')[:5],
        'bid_requests': bid_requests,
        'chart_data': chart_data,
    }
    return render(request, 'marketplace/dashboard.html', context)

