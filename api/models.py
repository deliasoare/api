from django.db import models
import base64
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Disability(models.Model):
    DISABILITY_CHOICES = [
        ('locomotor', 'Locomotor'),
        ('visual', 'Visual'),
        ('hearing', 'Hearing'),
        # Add other disability choices here
    ]
    
    name = models.CharField(max_length=100, choices=DISABILITY_CHOICES)
    severity = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])

    def __str__(self):
        return self.name

class Food_type(models.Model):
    TYPE_CHOICES = [
        ('italian', 'Italian'), 
        ('pizza', 'Pizza'),
        ('pasta', 'Pasta')
        # Add other food type choices here
    ]
    
    name = models.CharField(max_length=100, choices=TYPE_CHOICES)
    
    def __str__(self):
        return self.name

class Business_facility(models.Model):
    FACILITY_CHOICES = [
        ('wramp', "Wheelchair ramp"),
        ('pool', 'Swimming pool')
    ]
    
    name = models.CharField(max_length=100, choices=FACILITY_CHOICES)


from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    disabilities = models.ManyToManyField(Disability, related_name="users", blank=True)  # Removed null=True
    food_preferences = models.ManyToManyField(Food_type, related_name="users", blank=True)  # Removed null=True
    phone_number = models.CharField(max_length=20, unique=False, blank=True, null=True)  # Retained null=True if you want to allow blank
    user_address = models.CharField(max_length=255, blank=True, null=True)  # Retained null=True if you want to allow blank
    profile_picture = models.ImageField(upload_to='user_images/', blank=True, null=True)

    # Many-to-many relationships don't need null=True; blank=True suffices
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)  
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set_permissions', blank=True)  

    def get_disabilities(self):
        return [disability.name for disability in self.disabilities.all()]  # Simplified list comprehension

    def serializer(self):
        return {
            "username": self.username,
            "email": self.email,
            "address": self.user_address,  # Fixed typo: "adress" -> "address"
            "disabilities": [{"name": disability.name, "severity": disability.severity} for disability in self.disabilities.all()],
            "foodPreferences": [food.name for food in self.food_preferences.all()],
            "reviews": [{"title": review.title, "content": review.content, "rating": review.rating, "date_time_posted": review.date_time_posted} for review in self.reviews.all()] if hasattr(self, 'reviews') else [],
            "favorites": [
                {
                    "name": business.name,
                    "owner_id": business.owner.id,
                    "price_rating": business.price_rating,
                    "business_type": business.get_business_type_display(),
                    "address": business.address,
                    "website": business.website,
                    "phone_number": business.phone_number,
                    "rating": business.rating,
                    "locomotor_rating": business.locomotor_rating,
                    "visual_rating": business.visual_rating,
                    "hearing_rating": business.hearing_rating,
                    "reviews": [
                        {
                            "title": review.title,
                            "content": review.content,
                            "rating": review.rating,
                            "date_time_posted": review.date_time_posted
                        } for review in business.reviews.all()
                    ] if hasattr(business, 'reviews') else [],
                    "images": [
                        {
                            "url": image.url,
                            "caption": image.caption
                        } for image in business.images.all()
                    ] if hasattr(business, 'images') else []
                }
                for business in self.favorites.all()
            ]
        }

    
class Business(models.Model):
    BUSINESS_CHOICES = [
        ('hotel', "Hotel"),
        ('restaurant', 'Restaurant'),
        # Add other business type choices here
    ]
    
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, verbose_name=_("Owner"), on_delete=models.CASCADE)
    price_rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    business_type = models.CharField(max_length=10, choices=BUSINESS_CHOICES)
    address = models.CharField(max_length=255)
    website = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, unique=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    locomotor_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    visual_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    hearing_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    favorited_by = models.ManyToManyField(User, related_name='favorites', blank=True)

    def serializer(self):
        images = Image.objects.filter(business=self)
        reviews = Business_review.objects.filter(business=self)

        serialized_reviews = [review.serializer() for review in reviews]

        # Convert binary images to base64
        # serialized_images = [
        #     {
        #         "id": image.id,
        #         "name": image.name,
        #         "image": base64.b64encode(image.image).decode('utf-8')
        #     } for image in images
        # ]



        return {
            "name": self.name,
            "owner_id": self.owner.id,
            "price_rating": self.price_rating,
            "business_type": self.get_business_type_display(),
            "address": self.address,
            "website": self.website,
            "phone_number": self.phone_number,
            "rating": (self.rating), 
            "locomotor_rating": (self.locomotor_rating),
            "visual_rating": (self.visual_rating), 
            "hearing_rating": self.hearing_rating, 
            "reviews": serialized_reviews,
            "images": images,
        }

    def __str__(self):
        return f"{self.name} - ID:{self.id}"

class Image(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True)  # Optional name for the image
    image = models.ImageField(upload_to='business_images/', blank=True, default="")

# # !!! makemigrations da eroare ca cica trebe pentr ImageField ceva librarie Pillow care imi da eroare la instalare, in caz ca nu ampuc maine, poate reusiti sa rezolvati ca e 11 noaptea, mor de somn  si nu mai am nervii sa ma mai chinui !!!
# class Business_picture(models.Model):
#     business = models.ForeignKey(Business, on_delete=models.CASCADE)
#     image = models.ImageField()

# class Image(models.Model):
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True)
#     image = models.BinaryField()

class Business_review(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="reviews")
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)])
    locomotor_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    visual_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    hearing_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MaxValueValidator(5), MinValueValidator(1)])
    date_time_posted = models.DateTimeField(auto_now_add=True)
    users_liked = models.ManyToManyField(User, related_name="liked_reviews")

    def serializer(self):
        return {
            "creator": {
                "username": self.creator.username,
                "email": self.creator.email
            },
            "business": {
                "name": self.business.name,
                "owner": self.business.owner.username
            },
            "title": self.title,
            "content": self.content,
            "rating": self.rating,
            "locomotor_rating": self.locomotor_rating,
            "visual_rating": self.visual_rating,
            "hearing_rating": self.hearing_rating,
            "date_time_posted": self.date_time_posted.isoformat(),
            "users_liked": [{"username": user.username, "email": user.email} for user in self.users_liked.all()]
        }
        
class User_Business_visits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visits", null=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="visitors", null=True, blank=True)
    
