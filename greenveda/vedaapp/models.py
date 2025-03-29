# petdbapp/models.py
import datetime
from django.contrib.auth.models import User  # Import the User model
from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model

# models.py
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('packaged', 'Packaged'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    # ... other fields
    
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('PlantMaster', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
# CategoryMaster model: Represents product categories (e.g., types of pet grooming services or products)
from django.db import models

class CategoryMaster(models.Model):
    catID = models.AutoField(primary_key=True)  # Unique identifier for the category
    catName = models.CharField(max_length=18, unique=True)  # Prevents duplicate categories
    parent = models.ForeignKey(
        'self',  # Self-referential relationship
        on_delete=models.CASCADE,  # Deletes subcategories if parent is deleted
        blank=True,
        null=True,
        related_name='subcategories'  # Helps in querying subcategories easily
    )
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # Image for category

    def __str__(self):
        return f"{self.parent.catName} -> {self.catName}" if self.parent else self.catName


# ProductMaster model: Represents the products offered in the store (e.g., pet grooming products)
class PlantMaster(models.Model):
    name = models.CharField(max_length=100)  # Name of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # Image of the product
    description = RichTextField(blank=False, null=False)  # Detailed product description using CKEditor
    category = models.ForeignKey(CategoryMaster, related_name='products', on_delete=models.CASCADE)  # Product category
    
    def __str__(self):
        return self.name


# ProductGallery model: Stores images of products in addition to the main product image
class PlantGallery(models.Model):
    PGID = models.AutoField(primary_key=True)  # Unique identifier for the gallery image
    productPhoto = models.ImageField(upload_to='products/', null=True, blank=True)  # Additional product images
    productID = models.ForeignKey(PlantMaster, on_delete=models.CASCADE)  # The product this image belongs to

    def __str__(self):
        return f"Gallery for {self.productID.name}"





# CustomerMaster model: Stores customer details for booking and service history
class CustomerMaster(models.Model):
    customerID = models.AutoField(primary_key=True)  # Unique customer identifier
    customerName = models.CharField(max_length=255)  # Name of the customer
    email = models.EmailField()  # Customer's email address
    contact = models.CharField(max_length=15)  # Customer's contact number
    address = models.TextField()  # Customer's address
    username = models.CharField(max_length=255)  # Customer's username for login
    pincode = models.CharField(max_length=6)  # Customer's pincode for location

    def __str__(self):
        return self.customerName




# CartMaster model: Represents the customer's cart with selected products
class CartMaster(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)  # The user who owns the cart
    product = models.ForeignKey('PlantMaster', on_delete=models.CASCADE)  # The product in the cart
    qty = models.IntegerField(default=1)  # Quantity of the product
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # Subtotal for this item (price * qty)

    def __str__(self):
        return f"Cart item: {self.product.name} (Qty: {self.qty})"






# UserMaster model: Represents custom user information (alternative to Django's built-in User model)
class UserMaster(models.Model):
    userID = models.AutoField(primary_key=True)  # Unique user identifier
    userName = models.CharField(max_length=255)  # User's name
    email = models.EmailField()  # User's email address
    contact = models.CharField(max_length=15)  # User's contact number
    password = models.CharField(max_length=255)  # User's password (stored securely)

    def __str__(self):
        return self.userName




class StockMaster(models.Model):
    stockID = models.AutoField(primary_key=True)
    itemName = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)  # Current stock quantity
    price = models.DecimalField(max_digits=10, decimal_places=2)
    supplierName = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.itemName


from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.safestring import mark_safe


class PurchaseMaster(models.Model):
    purchaseID = models.AutoField(primary_key=True)
    stock = models.ForeignKey('StockMaster', on_delete=models.CASCADE, related_name='purchases')
    quantityPurchased = models.PositiveIntegerField()  # Ensures only positive quantities are allowed
    purchasePrice = models.DecimalField(max_digits=10, decimal_places=2)
    purchasedBy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    purchaseDate = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-purchaseDate']  # Orders purchases by most recent date
        verbose_name = "Purchase Record"
        verbose_name_plural = "Purchase Records"

    def save(self, *args, **kwargs):
        if self.pk:
            # Update operation: Adjust stock quantity based on the difference
            previous_instance = PurchaseMaster.objects.get(pk=self.pk)
            quantity_difference = self.quantityPurchased - previous_instance.quantityPurchased
        else:
            # Create operation: Directly add the quantity purchased
            quantity_difference = self.quantityPurchased

        # Update the stock quantity
        self.stock.quantity += quantity_difference
        self.stock.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.stock.quantity -= self.quantityPurchased
        self.stock.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        purchased_by = self.purchasedBy.username if self.purchasedBy else "Unknown"
        return f"{self.stock.itemName} purchased by {purchased_by} on {self.purchaseDate.strftime('%Y-%m-%d')}"

    @property
    def subtotal(self):
        return self.quantityPurchased * self.purchasePrice




from django.db import models

class Feature(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='features/', blank=True, null=True)

    def __str__(self):
        return self.title

class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id} → {self.status}"

# models.pyfrom django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    LANGUAGE_CHOICES = [
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('Punjabi', 'Punjabi'),
        ('Bengali', 'Bengali'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Marathi', 'Marathi'),
        ('Gujarati', 'Gujarati'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='User Profile'
    )
    avatar = models.ImageField(
        upload_to='profile_images/', 
        null=True, 
        blank=True,
        verbose_name='Profile Picture'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(null=True, blank=True, verbose_name='Date of Birth')
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def handle_user_profile(sender, instance, created, **kwargs):
    """
    Combined signal handler that both creates and saves the profile
    """
    UserProfile.objects.get_or_create(user=instance)
    if hasattr(instance, 'profile'):
        instance.profile.save()