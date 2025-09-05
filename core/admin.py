from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'type', 'phone1', 'phone2', 'is_owner', 'is_staff_user', 'is_active', 'is_superuser')
    list_filter = ('type', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone1', 'phone2')
    ordering = ('username',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('type', 'phone1', 'phone2', 'address')
        }),
    )

    readonly_fields = ('is_owner', 'is_staff_user')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role')
    list_filter = ('company',)
    search_fields = ('user__username', 'company__name', 'role')

@admin.register(Warp)
class WarpAdmin(admin.ModelAdmin):
    list_display = ('design','name', 'weaver', 'warp_yarn','date_start_warper','date_start_weaver', 'length', 'meters', 'isComplected','isWarped')
    list_filter = ('design','isComplected','isWarped')
    search_fields = ('name', 'weaver__username','warper__username', 'user__username')
    ordering = ('-date_start_warper','-date_start_weaver')


@admin.register(Wage)
class WageAdmin(admin.ModelAdmin):
    list_display = ('warp', 'date', 'wage_good', 'wage_demage', 'wage_extra')
    list_filter = ('date',)
    search_fields = ('warp__name', 'user__username')
    
    
    

@admin.register(Piece)
class PieceAdmin(admin.ModelAdmin):
    list_display = ('id', 'warp', 'date', 'count', 'length', 'type', 'get_weaver')
    list_filter = ('date', 'type', 'warp__weaver__username')
    search_fields = ('warp__name', 'warp__weaver__username')
    list_select_related = ('warp',)

    def get_weaver(self, obj):
        return obj.warp.weaver.username
    get_weaver.short_description = 'Weaver'

    # Optional: Order by date descending
    ordering = ('-date',)
    
    
    

@admin.register(Transactions)
class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'staff', 'date', 'amount', 'note')
    list_filter = ('date', 'company', 'staff')
    search_fields = ('note', 'user__username', 'company__name')
    date_hierarchy = 'date'
    ordering = ('-date',)

    fieldsets = (
        (None, {
            'fields': ('company', 'staff', 'date', 'amount', 'note')
        }),
    )

@admin.register(Yarn)
class YarnAdmin(admin.ModelAdmin):
    list_display = ('company', 'color', 'count')
    list_filter = ('company', 'color', 'count')
    search_fields = ('color',) 

    fieldsets = (
        (None, {
            'fields': ('company', 'color', 'count', 'color_code')
        }),
    )

@admin.register(Yarn_Transactions)
class YarnTransactionsAdmin(admin.ModelAdmin):
    list_display = ('yarn', 'date', 'quantity', 'warp', 'transaction_type', 'note') 
    list_filter = ('date', 'warp', 'transaction_type', 'yarn__color') 
    search_fields = ('yarn__color', 'warp__name', 'note')
    
    fieldsets = (
        (None, {
            'fields': ('yarn', 'date', 'quantity', 'transaction_type', 'warp', 'note') # Reordered fields for flow
        }),
    )

@admin.register(WarpDesign)
class WarpDesignAdmin(admin.ModelAdmin):
    list_display = ('company','name')
    list_filter = ('company','name')
    fieldsets = (
        (None,{
            'fields' : ('company','name')
        }),
    )

@admin.register(WarpDesignEntry)
class WarpDesignEntryAdmin(admin.ModelAdmin):
    list_display =('order','warp_design','yarn','lint_count','color')
    list_filter = ('warp_design','yarn','lint_count')
    fieldsets = (
        (None,{
            'fields' : ('order','warp_design','yarn','lint_count','color')
        }),
    )