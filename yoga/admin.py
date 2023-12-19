from django.contrib import admin
from .models import *

# Register your models here.

# Registering the YogaBatch model with the admin interface
admin.site.register(YogaBatch)

# Registering the YogaBooking model with the admin interface
admin.site.register(YogaBooking)

# Registering the Offer model with the admin interface
admin.site.register(Offer)

# Registering the YogaTimings model with the admin interface
admin.site.register(YogaTimings)

# Registering the Order model with the admin interface
admin.site.register(Order)