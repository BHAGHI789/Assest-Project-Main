from django.contrib import admin
from .models import Employee, Details, Assigned, ProductAssigned

admin.site.register(Employee)

class DetailsAdmin(admin.ModelAdmin):
    list_display = ['id','make','modelno','description','units','date']
admin.site.register(Details,DetailsAdmin)

class AssingnedAdmin(admin.ModelAdmin):
    list_display = ['employee','details','date']
admin.site.register(Assigned,AssingnedAdmin)


@admin.register(ProductAssigned)
class ProductAssignedAdmin(admin.ModelAdmin):
    list_display = ('make', 'modelno','units', 'assigned_text', 'assigned_date')
    list_filter = ('assigned_date',)
