from django.contrib import admin
import os
from django import forms
from django.conf import settings
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

class AvailableCategoryTemplateForm(forms.ModelForm):
    class Meta:
        model = AvailableCategoryTemplate
        fields = '__all__'

    def __init__(self, *args, **kwargs):  
        super().__init__(*args, **kwargs) 
        
        icons_dir = os.path.join(settings.BASE_DIR, 'static', 'icons')
        
        choices = []
        if os.path.exists(icons_dir):
            files = sorted(os.listdir(icons_dir))
            for f in files:
                if f.endswith(('.png', '.svg', '.jpg', '.jpeg')):
                    choices.append((f, f))  
        
        if not choices:
            choices = [('wallet1.png', 'wallet1.png')]
            
        self.fields['icon_name'] = forms.ChoiceField(
            choices=choices, 
            label="Выберите файл иконки из static/icons/",
            initial='wallet1.png'
        )

@admin.register(AvailableCategoryTemplate)
class AvailableCategoryTemplateAdmin(admin.ModelAdmin):
    form = AvailableCategoryTemplateForm
    list_display = ('name', 'type', 'color_hex', 'icon_name')
    
@admin.register(AvailableBank)
class AvailableBankAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color_hex')
    search_fields = ('name',)