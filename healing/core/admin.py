from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import Usuario, Auditoria


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'perfil', 'is_active']
    list_filter = ['perfil', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil Healing', {'fields': ('perfil',)}),
    )


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ['operacao', 'tabela_afetada', 'usuario', 'executado_em']
    list_filter = ['operacao', 'tabela_afetada']
    readonly_fields = ['usuario', 'tabela_afetada', 'operacao', 'dados_anteriores', 'executado_em']
