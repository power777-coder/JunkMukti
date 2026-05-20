from django.urls import path
from .views import (
    home, upload_waste, marketplace, my_listings, waste_detail,
    edit_waste, delete_waste, add_to_wishlist, remove_from_wishlist,
    wishlist, add_review, send_message, request_purchase, mark_sold,
    inbox, user_profile, dashboard, transactions,
    place_bid, accept_bid, nearby
)

urlpatterns = [
    path('', home, name='home'),
    path('upload/', upload_waste, name='upload_waste'),
    path('marketplace/', marketplace, name='marketplace'),
    path('my-listings/', my_listings, name='my_listings'),
    path('waste/<int:waste_id>/', waste_detail, name='waste_detail'),
    path('waste/<int:waste_id>/edit/', edit_waste, name='edit_waste'),
    path('waste/<int:waste_id>/delete/', delete_waste, name='delete_waste'),
    path('waste/<int:waste_id>/wishlist/add/', add_to_wishlist, name='add_to_wishlist'),
    path('waste/<int:waste_id>/wishlist/remove/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', wishlist, name='wishlist'),
    path('waste/<int:waste_id>/review/', add_review, name='add_review'),
    path('waste/<int:waste_id>/message/', send_message, name='send_message'),
    path('waste/<int:waste_id>/request-purchase/', request_purchase, name='request_purchase'),
    path('waste/<int:waste_id>/place-bid/', place_bid, name='place_bid'),
    path('waste/<int:waste_id>/accept-bid/<int:bid_id>/', accept_bid, name='accept_bid'),
    path('waste/<int:waste_id>/mark-sold/', mark_sold, name='mark_sold'),
    path('transactions/', transactions, name='transactions'),
    path('nearby/', nearby, name='nearby'),
    path('inbox/', inbox, name='inbox'),
    path('user/<int:user_id>/', user_profile, name='user_profile'),
    path('dashboard/', dashboard, name='dashboard'),
]

