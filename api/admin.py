from django.contrib import admin
from .models import User, Disability, Food_type, Business_facility, Business, Business_review, Image
from django.contrib.sessions.models import Session

class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'session_data', 'expire_date')  # Removed 'created'


# Register your models here.

class BusinessImageInline(admin.TabularInline):
    model = Image
    extra = 1  # Allow one additional image upload by default

class BusinessAdmin(admin.ModelAdmin):
    inlines = [BusinessImageInline]

admin.site.register(User)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Business_review)
admin.site.register(Business_facility)
admin.site.register(Food_type)
admin.site.register(Image)
admin.site.register(Disability)
admin.site.register(Session, SessionAdmin)


