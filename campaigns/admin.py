from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
# Register your models here.
from campaigns.models import (
	Category,
	Campaign,
	Organization,
)

class CampaignAdmin(SummernoteModelAdmin):
	summernote_fields=('description',)


admin.site.register(Campaign)
admin.site.register(Category)
admin.site.register(Organization)