from django.contrib import admin
from .models import Account, Category, Tag, Transaction, RecurringTransaction, Goal, Budget, Notification, AvailableCategoryTemplate, AvailableBank

# Register your models here.
admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Transaction)
admin.site.register(RecurringTransaction)
admin.site.register(Goal)
admin.site.register(Budget)
admin.site.register(Notification)

@admin.register(AvailableCategoryTemplate)
class AvailableCategoryTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'color') 
    list_filter = ('type',)
    search_fields = ('name',)
    
@admin.register(AvailableBank)
class AvailableBankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'logo_name')
    search_fields = ('name',)