from django.contrib import admin

from ads.models import Advertisement, Category, SubCategory


admin.site.register(Advertisement)
admin.site.register(Category)
admin.site.register(SubCategory)