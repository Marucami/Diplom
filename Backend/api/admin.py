from django.contrib import admin
from .models import Account, Category, Tag, Transaction, RecurringTransaction, Goal, Budget, Notification

# Register your models here.
admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Transaction)
admin.site.register(RecurringTransaction)
admin.site.register(Goal)
admin.site.register(Budget)
admin.site.register(Notification)