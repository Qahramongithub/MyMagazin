from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from rangefilter.filters import DateRangeFilter
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.models import User, Warehouse
from django.db import models


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'created_at', 'superuser_start_date', 'superuser_end_date')
    list_filter = (
        ('superuser_start_date', DateRangeFilter), ('superuser_end_date', DateRangeFilter),
        'role', 'username'
    )
    formfield_overrides = {
        models.DateField: {'widget': AdminDateWidget},
    }
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'role', 'superuser_start_date', 'superuser_end_date')}),
        ('Status', {'fields': ('is_active',)}),
    )

    def save_model(self, request, obj, form, change):
        """
        Faqat yangi user yaratilsa yoki mavjud user paroli o‘zgartirilsa,
        passwordni hash qilish.
        """
        if not change or 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_users', 'created_at')
    filter_horizontal = ('user',)
    list_filter = (('created_at', DateRangeFilter),)
    search_fields = ('name',)

    def get_users(self, obj):
        return ", ".join([str(u) for u in obj.user.all()])

    get_users.short_description = 'Users'


from django.contrib.auth.models import Group

# admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)
