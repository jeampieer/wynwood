from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified")
    list_filter = ("is_active", "created")
