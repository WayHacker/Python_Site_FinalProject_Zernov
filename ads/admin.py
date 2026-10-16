from django.contrib import admin

from .models import Ad, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner', 'city', 'price_per_day',
        'status', 'is_active', 'created_at',
    )
    list_filter = ('status', 'city', 'category', 'is_active')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_ads', 'reject_ads', 'archive_ads']

    @admin.action(description='✅ Одобрить выбранные')
    def approve_ads(self, request, queryset):
        updated = queryset.update(status=Ad.Status.APPROVED, moderation_comment='')
        self.message_user(request, f'Одобрено: {updated}')

    @admin.action(description='❌ Отклонить выбранные')
    def reject_ads(self, request, queryset):
        updated = queryset.update(
            status=Ad.Status.REJECTED,
            moderation_comment='Не соответствует правилам сайта.',
        )
        self.message_user(request, f'Отклонено: {updated}')

    @admin.action(description='📦 В архив')
    def archive_ads(self, request, queryset):
        updated = queryset.update(status=Ad.Status.ARCHIVED, is_active=False)
        self.message_user(request, f'В архиве: {updated}')
