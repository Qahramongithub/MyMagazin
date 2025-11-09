from django.contrib import admin
from rangefilter.filters import DateRangeFilter
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from apps.models import Warehouse


# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'role', 'created_at', 'superuser_start_date', 'superuser_end_date')
#     list_filter = (
#         ('superuser_start_date', DateRangeFilter), ('superuser_end_date', DateRangeFilter),
#         'role', 'username'
#     )
#     formfield_overrides = {
#         models.DateField: {'widget': AdminDateWidget},
#     }
#     search_fields = ('username', 'email')
#     ordering = ('username',)
#     fieldsets = (
#         (None, {'fields': ('username', 'email', 'role', 'superuser_start_date', 'superuser_end_date')}),
#         ('Status', {'fields': ('is_active',)}),
#     )


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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User  # yoki CustomUser


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("username", "email", "is_staff", "is_active", "role", "superuser_start_date", "superuser_end_date")
    list_filter = ("is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "email", "password", "role", "superuser_start_date", "superuser_end_date")}),
        ("Permissions", {"fields": ("is_active",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "is_staff", "is_active", "groups", "user_permissions"),
        }),
    )

    search_fields = ("username", "email")
    ordering = ("username",)

