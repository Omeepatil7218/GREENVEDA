from django.contrib import admin
from django.utils.html import format_html,strip_tags
from django.db import models
from ckeditor.widgets import CKEditorWidget
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import CategoryMaster, PlantGallery, PlantMaster,StockMaster, PurchaseMaster
#######################################################################################################################

from django.contrib import admin
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import path
from .models import Order

class RejectionForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea)

@admin.action(description='Mark selected orders as accepted')
def make_accepted(modeladmin, request, queryset):
    queryset.update(status='accepted')

@admin.action(description='Mark selected orders as packaged')
def make_packaged(modeladmin, request, queryset):
    queryset.update(status='packaged')

@admin.action(description='Mark selected orders as shipped')
def make_shipped(modeladmin, request, queryset):
    queryset.update(status='shipped')

@admin.action(description='Mark selected orders as delivered')
def make_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')

from django.contrib import messages
from django import forms

class RejectionForm(forms.Form):
    reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))

@admin.action(description='Reject selected orders')
def reject_orders(modeladmin, request, queryset):
    if 'reason' in request.POST:
        form = RejectionForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            count = queryset.count()
            queryset.update(status='rejected', rejection_reason=reason)
            modeladmin.message_user(request, f"Rejected {count} order(s). Reason: {reason}", messages.SUCCESS)
            return
    else:
        form = RejectionForm()

    # Show form in the same page using messages
    html = f"""
    <form method="post" action="">
        {form.as_p()}
        <input type="hidden" name="action" value="reject_orders" />
        <input type="submit" name="confirm" value="Confirm Rejection" class="default" style="float: none;">
        <input type="submit" name="cancel" value="Cancel" class="default" style="float: none; margin-left: 10px;">
    </form>
    """
    
    modeladmin.message_user(request, html, extra_tags='safe')
    return
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at', 'rejection_reason']
    list_filter = ['status']
    actions = [make_accepted, make_packaged, make_shipped, make_delivered, reject_orders]
    
    # Add rejection reason to change form
    fieldsets = (
        (None, {
            'fields': ('user', 'items', 'total_price', 'status')
        }),
        ('Rejection Details', {
            'fields': ('rejection_reason',),
            'classes': ('collapse',),
        }),
    )

admin.site.register(Order, OrderAdmin)



class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('name_with_image_hover', 'price', 'short_description', 'category')
    search_fields = ('name', 'description', 'category__catName')
    list_filter = ('price', 'category')
    actions = ['redirect_to_update']

    # Remove <p> tags and other HTML from the description in the admin display
    def short_description(self, obj):
        if obj.description:
            plain_text = strip_tags(obj.description).replace('<p>', '').replace('</p>', '')
            return plain_text[:50] + "..." if len(plain_text) > 50 else plain_text
        return ""
    short_description.short_description = 'Description'

    # Hover effect with product image on name
    def name_with_image_hover(self, obj):
        if obj.image:
            return format_html(
                '''
                <div class="product-hover-container" style="position:relative; display:inline-block;">
                    <span style="cursor: pointer;" title="{}">{}</span>
                    <img src="{}" class="hover-image" style="display:none; position:absolute; top:100%; left:0; z-index:10; border:1px solid #ccc; width:150px; height:150px; background:white; border-radius:5px;" />
                </div>
                ''',
                obj.name,
                obj.name,
                obj.image.url,
            )
        return obj.name
    name_with_image_hover.short_description = 'Name'
    name_with_image_hover.admin_order_field = 'name'

    # Enable CKEditor and remove <p> tags automatically
    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget(config_name='default')},
    }

    class Media:
        js = (
            '//cdn.ckeditor.com/4.16.2/standard/ckeditor.js',
            '''document.addEventListener('DOMContentLoaded', function() {
                if (typeof CKEDITOR !== 'undefined') {
                    CKEDITOR.on('instanceReady', function(event) {
                        event.editor.setData(event.editor.getData().replace(/<p>/g, '').replace(/<\/p>/g, ''));
                        event.editor.config.enterMode = CKEDITOR.ENTER_BR;
                        event.editor.config.shiftEnterMode = CKEDITOR.ENTER_BR;
                    });
                }
            });''',
        )
        css = {
            'all': (
                '''
                .product-hover-container:hover .hover-image {
                    display: block;
                }
                .product-hover-container span {
                    text-decoration: underline;
                }
                ''',
            ),
        }

    # Redirect to update page for a single product
    def redirect_to_update(self, request, queryset):
        if queryset.count() == 1:
            obj = queryset.first()
            update_url = reverse('admin:petapp_productmaster_change', args=[obj.id])
            return HttpResponseRedirect(update_url)
        self.message_user(request, "Please select exactly one item to update.", level='warning')

    redirect_to_update.short_description = "Update selected item"

# Register ProductMaster model
admin.site.register(PlantMaster, ProductMasterAdmin)




###########################################################################################################################
# Register CategoryMaster model
from django.contrib import admin
from django.utils.html import mark_safe
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CategoryMaster

@admin.register(CategoryMaster)
class CategoryMasterAdmin(admin.ModelAdmin):
    list_display = ('catName', 'parent', 'display_image')  
    search_fields = ('catName',)
    list_filter = ('parent',)  # Allows filtering by parent category
    actions = ['redirect_to_update']

    # Display Image in Admin Panel
    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No image"
    display_image.short_description = 'Image'

    # Prevent duplicate categories
    def save_model(self, request, obj, form, change):
        if not change and CategoryMaster.objects.filter(catName=obj.catName).exists():
            raise ValidationError("A category with this name already exists.")
        super().save_model(request, obj, form, change)

    # Only allow subcategories under "Medicines"
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['parent'].queryset = CategoryMaster.objects.all()
        return form

    # Custom action to redirect to update page
    def redirect_to_update(self, request, queryset):
        if queryset.count() == 1:
            obj = queryset.first()
            update_url = reverse('admin:petapp_categorymaster_change', args=[obj.pk])
            return HttpResponseRedirect(update_url)
        self.message_user(request, "Please select exactly one item to update.", level='warning')

    redirect_to_update.short_description = "Update selected item"

    # Admin Panel Styling
    class Media:
        css = {
            'all': (
                '''
                .button {
                    padding: 5px 10px;
                    background-color: #28a745;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                    font-size: 12px;
                }
                .button:hover {
                    background-color: #218838;
                }
                .model-categorymaster td {
                    text-align: center;
                }
                ''',
            ),
        }

#########################################################################################################################
# Register ProductGallery model
@admin.register(PlantGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('PGID', 'product_image_preview', 'productID')  # Remove update_button from list_display
    list_filter = ('productID__name',)  # Correctly filter by 'name' field of ProductMaster
    search_fields = ('productID__name',)  # Correctly search by 'name' field of ProductMaster
    actions = ['redirect_to_update']  # Add custom action to update

    # Add "Update" action to dropdown
    def redirect_to_update(self, request, queryset):
        if queryset.count() == 1:  # Ensure only one item is selected
            obj = queryset.first()
            update_url = reverse('admin:petapp_productgallery_change', args=[obj.PGID])  # Replace 'petapp' with your app's name
            return HttpResponseRedirect(update_url)
        self.message_user(request, "Please select exactly one item to update.", level='warning')

    redirect_to_update.short_description = "Update selected item"

    # Display product image preview
    def product_image_preview(self, obj):
        if obj.productPhoto and hasattr(obj.productPhoto, 'url'):
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.productPhoto.url)
        return "No Image"

    product_image_preview.short_description = "Image Preview"

    # Add internal JavaScript and CSS for the button if needed (optional)
    class Media:
        css = {
            'all': (
                '''
                .button {
                    padding: 5px 10px;
                    background-color: #28a745;
                    color: white;
                    text-decoration: none;
                    border-radius: 3px;
                    font-size: 12px;
                }
                .button:hover {
                    background-color: #218838;
                }
                ''',
            ),
        }


#########################################################################################################################



@admin.register(StockMaster)
class StockMasterAdmin(admin.ModelAdmin):
    list_display = ('itemName', 'initial_stock', 'quantity', 'sold_quantity', 'stock_status', 'price', 'supplierName')
    list_filter = ('supplierName',)
    search_fields = ('itemName',)
    readonly_fields = ('initial_stock', 'sold_quantity', 'stock_status')
    
    # Set initial stock to 100 for all products
    def initial_stock(self, obj):
        return 100
    initial_stock.short_description = 'Initial Stock'
    
    # Calculate sold quantity
    def sold_quantity(self, obj):
        return 100 - obj.quantity
    sold_quantity.short_description = 'Sold Quantity'
    
    # Stock status with colors
    def stock_status(self, obj):
        if obj.quantity == 0:
            return format_html('<span style="color: red; font-weight: bold;">SOLD OUT</span>')
        elif obj.quantity < 20:
            return format_html('<span style="color: orange; font-weight: bold;">LOW STOCK ({} left)</span>', obj.quantity)
        return format_html('<span style="color: green; font-weight: bold;">IN STOCK ({} left)</span>', obj.quantity)
    stock_status.short_description = 'Status'
    
    # Initialize stock when new item is added
    def save_model(self, request, obj, form, change):
        if not change:  # Only for new items
            obj.quantity = 100  # Set initial stock
        super().save_model(request, obj, form, change)

from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from .models import PurchaseMaster




@admin.register(PurchaseMaster)
class PurchaseMasterAdmin(admin.ModelAdmin):
    list_display = ('stock', 'quantityPurchased', 'purchasePrice', 'total_cost', 'purchasedBy', 'purchaseDate')
    search_fields = ('stock__itemName', 'purchasedBy__username')
    readonly_fields = ('total_cost', 'purchaseDate')

    fieldsets = (
        (None, {
            'fields': ('stock', 'quantityPurchased', 'purchasePrice', 'purchasedBy'),
        }),
        ('Additional Info', {
            'fields': ('purchaseDate',),
        }),
    )

    def total_cost(self, obj):
        return obj.quantityPurchased * obj.purchasePrice
    total_cost.short_description = 'Total Cost'

    def render_change_form(self, request, context, *args, **kwargs):
        """
        Inject inline CSS and JS directly into the admin page for PurchaseMaster.
        """
        context['adminform'].form.fields['quantityPurchased'].widget.attrs.update({
            'oninput': 'updateSubtotal()',
            'style': 'width: 100px; margin-right: 10px;',
        })
        context['adminform'].form.fields['purchasePrice'].widget.attrs.update({
            'oninput': 'updateSubtotal()',
            'style': 'width: 100px; margin-right: 10px;',
        })

        # Inline JavaScript and CSS
        context['inline_css_js'] = mark_safe("""
        <style>
            .subtotal-display {
                margin-top: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            .stock-warning {
                color: red;
                font-weight: bold;
                margin-top: 10px;
            }
        </style>
        <script>
            function updateSubtotal() {
                const quantityInput = document.getElementById('id_quantityPurchased');
                const priceInput = document.getElementById('id_purchasePrice');
                const stockInput = document.getElementById('id_stock');
                let subtotalDisplay = document.getElementById('subtotal-display');
                let warningDisplay = document.getElementById('stock-warning');

                if (!subtotalDisplay) {
                    subtotalDisplay = document.createElement('div');
                    subtotalDisplay.id = 'subtotal-display';
                    subtotalDisplay.className = 'subtotal-display';
                    quantityInput.closest('fieldset').appendChild(subtotalDisplay);
                }

                if (!warningDisplay && stockInput) {
                    warningDisplay = document.createElement('div');
                    warningDisplay.id = 'stock-warning';
                    warningDisplay.className = 'stock-warning';
                    quantityInput.closest('fieldset').appendChild(warningDisplay);
                }

                const quantity = parseFloat(quantityInput.value) || 0;
                const price = parseFloat(priceInput.value) || 0;
                subtotalDisplay.textContent = `Subtotal: ₹ ${(quantity * price).toFixed(2)}`;
                
                if (stockInput && warningDisplay) {
                    const selectedStockId = stockInput.value;
                    if (selectedStockId) {
                        fetch(`/admin/vedaapp/stockmaster/${selectedStockId}/`)
                            .then(response => response.json())
                            .then(data => {
                                if (quantity > data.quantity) {
                                    warningDisplay.textContent = `Warning: Only ${data.quantity} items available!`;
                                } else {
                                    warningDisplay.textContent = '';
                                }
                            });
                    }
                }
            }

            document.addEventListener('DOMContentLoaded', function() {
                updateSubtotal();
                if (document.getElementById('id_stock')) {
                    document.getElementById('id_stock').addEventListener('change', updateSubtotal);
                }
            });
        </script>
        """)

        return super().render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.purchasedBy:
            obj.purchasedBy = request.user
        if not obj.purchaseDate:
            obj.purchaseDate = now()
            
        # Update stock quantity
        stock = obj.stock
        stock.quantity -= obj.quantityPurchased  # Decrease stock when purchased
        stock.save()
        
        super().save_model(request, obj, form, change)

from .models import Feature

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')



from django.contrib import admin
from .models import PlantMaster

# Unregister if already registered
try:
    admin.site.unregister(PlantMaster)
except admin.sites.NotRegistered:
    pass

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'add_to_cart_link')

    def add_to_cart_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('add_to_cart', args=[obj.id])
        return format_html('<a href="{}" target="_blank">Add to Cart</a>', url)

    add_to_cart_link.short_description = 'Add to Cart'

# Register again
admin.site.register(PlantMaster, ProductAdmin)
