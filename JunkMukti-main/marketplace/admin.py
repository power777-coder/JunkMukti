from django.contrib import admin
from .models import Waste
from django.utils.html import format_html


@admin.register(Waste)
class WasteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'waste_type',
        'weight_kg',
        'final_price',
        'image_preview',
        'created_at'
    )

    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" style="border-radius:8px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = "Image Preview"
