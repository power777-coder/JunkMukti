from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.db.models import Avg


class Waste(models.Model):

    WASTE_TYPE_CHOICES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('metal', 'Metal'),
        ('glass', 'Glass'),
        ('organic', 'Organic'),
        ('electronics', 'Electronics'),
        ('wood', 'Wood'),
        ('textile', 'Textile'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='waste_items'
    )

    waste_type = models.CharField(
        max_length=20,
        choices=WASTE_TYPE_CHOICES
    )

    description = models.TextField()
    
    category = models.CharField(
        max_length=50,
        default='general'
    )

    weight_kg = models.FloatField()
    
    image = CloudinaryField(
        'image',
        blank=True,
        null=True
    )
    
    location = models.CharField(
        max_length=255,
        blank=True,
        default='Not specified'
    )

    predicted_price = models.FloatField(
        blank=True,
        null=True
    )

    final_price = models.FloatField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    views = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.waste_type} - {self.user.username}"
    
    def get_average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    waste = models.ForeignKey(Waste, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'waste')
    
    def __str__(self):
        return f"{self.user.username} - {self.waste.waste_type}"


class Review(models.Model):
    waste = models.ForeignKey(Waste, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('waste', 'reviewer')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.waste.waste_type} by {self.reviewer.username}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    waste = models.ForeignKey(Waste, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    waste = models.ForeignKey(Waste, on_delete=models.SET_NULL, null=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.id} - {self.waste.waste_type}"


class Bid(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    waste = models.ForeignKey(Waste, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bid {self.id} - {self.waste.waste_type} by {self.bidder.username}"
