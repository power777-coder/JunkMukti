# Installation & Setup Guide

## Step 1: Apply Database Migrations

Before running the app, create and apply migrations for the new models:

```bash
# Create migrations for new models
python manage.py makemigrations marketplace

# Apply migrations to database
python manage.py migrate marketplace
```

## Step 2: Update Django Settings (if needed)

Ensure your `settings.py` has these required apps:

```python
INSTALLED_APPS = [
    # ... existing apps ...
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'marketplace',
    'accounts',
    'cloudinary',
    'cloudinary_storage',
]
```

## Step 3: Static Files Configuration

Make sure your `settings.py` has proper static files configuration:

```python
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# For production
STATICFILES_STORAGE = 'cloudinary_storage.storage.StaticHashedCloudinaryStorage'
```

## Step 4: Update Main URLs

Ensure your main `urls.py` includes the marketplace URLs:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('marketplace.urls')),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Step 5: Update Marketplace Admin

Update `marketplace/admin.py` to show new models in Django Admin:

```python
from django.contrib import admin
from .models import Waste, WishlistItem, Review, Message, Transaction

@admin.register(Waste)
class WasteAdmin(admin.ModelAdmin):
    list_display = ('id', 'waste_type', 'user', 'weight_kg', 'final_price', 'status', 'created_at')
    list_filter = ('status', 'waste_type', 'created_at')
    search_fields = ('description', 'user__username')
    date_hierarchy = 'created_at'

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'waste', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'waste__description')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'waste', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__username', 'waste__description')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'waste', 'buyer', 'seller', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'seller__username')
```

## Step 6: Create Superuser (if not already created)

```bash
python manage.py createsuperuser
```

## Step 7: Collect Static Files (for production)

```bash
python manage.py collectstatic --noinput
```

## Step 8: Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## Testing the New Features

### 1. Test Waste Upload
- Go to `/upload/`
- Create a waste item with all details
- Verify it appears in marketplace

### 2. Test Marketplace Features
- Visit `/marketplace/`
- Try searching (e.g., "plastic")
- Try filtering by waste type
- Try sorting by price
- Click on any item to view details

### 3. Test Wishlist
- Click heart icon on waste card
- Visit `/wishlist/` to see saved items
- Remove items from wishlist

### 4. Test Messages
- Click "Contact Seller" on a waste detail page
- Send a message
- Go to `/inbox/` to view messages

### 5. Test Reviews
- Go to waste detail page
- Click "Write a Review"
- Leave a 5-star review with comment
- Verify review appears on page

### 6. Test Dashboard
- Go to `/dashboard/`
- Verify all stats are displayed
- Check recent listings
- Check recent reviews

### 7. Test User Profile
- Click on any username or seller name
- View seller's profile, ratings, and listings

---

## File Structure

Your updated project structure should look like:

```
JunkMukti-main/
├── marketplace/
│   ├── models.py (UPDATED - new models added)
│   ├── forms.py (UPDATED - enhanced forms)
│   ├── views.py (UPDATED - new views)
│   ├── urls.py (UPDATED - new routes)
│   ├── static/
│   │   └── marketplace/
│   │       └── css/
│   │           ├── style.css (original)
│   │           └── modern_style.css (NEW)
│   └── migrations/ (new migration files will be created)
├── templates/
│   ├── base.html (NEW - main layout)
│   ├── index.html (UPDATED)
│   └── marketplace/
│       ├── marketplace.html (UPDATED)
│       ├── waste_detail.html (NEW)
│       ├── upload_waste.html (UPDATED)
│       ├── my_listings.html (UPDATED)
│       ├── edit_waste.html (NEW)
│       ├── delete_waste.html (NEW)
│       ├── dashboard.html (NEW)
│       ├── wishlist.html (NEW)
│       ├── inbox.html (NEW)
│       ├── add_review.html (NEW)
│       ├── send_message.html (NEW)
│       └── user_profile.html (NEW)
├── accounts/
│   └── (existing auth templates)
├── MY_Project/
│   └── settings.py
├── IMPROVEMENTS.md (NEW - this file)
└── SETUP.md (NEW - setup guide)
```

---

## Troubleshooting

### Issue: Migration errors
**Solution**: 
```bash
python manage.py migrate --fake marketplace zero
python manage.py migrate marketplace
```

### Issue: Static files not loading
**Solution**:
```bash
python manage.py collectstatic
python manage.py collectstatic --clear
```

### Issue: Template not found
**Solution**: Ensure `'APP_DIRS': True` in TEMPLATES settings

### Issue: CSRF token missing
**Solution**: Add `{% csrf_token %}` in all POST forms

### Issue: Images not displaying
**Solution**: 
- Check Cloudinary configuration in settings.py
- Verify MEDIA_ROOT and MEDIA_URL settings
- Check file permissions

---

## Performance Tips

1. **Database Optimization**:
   - Add indexes for frequently queried fields
   - Use `select_related()` for ForeignKey queries
   - Use `prefetch_related()` for ManyToMany queries

2. **Caching**:
   - Cache marketplace listings
   - Cache user profile data
   - Cache most viewed waste items

3. **Image Optimization**:
   - Compress images before upload
   - Use Cloudinary transformations
   - Implement lazy loading

4. **Query Optimization**:
   ```python
   # Good:
   wastes = Waste.objects.select_related('user').filter(status='available')
   
   # Bad:
   wastes = Waste.objects.filter(status='available')
   for waste in wastes:
       username = waste.user.username  # N+1 query problem!
   ```

---

## Security Checklist

- ✅ CSRF protection enabled
- ✅ Authentication required for sensitive views
- ✅ Input validation on forms
- ✅ XSS protection with template escaping
- ✅ SQL injection prevention (using ORM)
- ✅ Owner verification for edit/delete operations
- ✅ Secure password hashing

---

## Deployment Considerations

1. Set `DEBUG = False` in production
2. Add proper ALLOWED_HOSTS
3. Use environment variables for secrets
4. Enable HTTPS
5. Set up proper logging
6. Configure error monitoring (Sentry)
7. Use CDN for static files
8. Implement rate limiting

---

## Questions or Issues?

Refer to:
- Django Documentation: https://docs.djangoproject.com/
- Bootstrap Documentation: https://getbootstrap.com/docs/5.0/
- Cloudinary: https://cloudinary.com/documentation

---

**Happy coding! 🚀**
