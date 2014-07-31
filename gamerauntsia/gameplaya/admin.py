from gamerauntsia.gameplaya.models import GamePlaya, Kategoria, Zailtasuna
from django.contrib import admin
from gamerauntsia.gameplaya.forms import GamePlayAdminForm

from datetime import datetime
from django.utils import timezone

class GamePlayAdmin(admin.ModelAdmin):
    list_display = ('izenburua', 'slug','zailtasuna', 'jokoa','pub_date', 'erabiltzailea','publikoa_da')
    prepopulated_fields = {"slug": ("izenburua",)}
    filter_horizontal = ('kategoria',)
    row_id_fields = ('argazkia','erabiltzailea')
    list_filter = ('erabiltzailea','zailtasuna', 'publikoa_da')
    search_fields = ['erabiltzailea__fullname','erabiltzailea__username','izenburua']
    form = GamePlayAdminForm
    
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('izena','slug')
    prepopulated_fields = {"slug": ("izena",)}
    
class ZailtasunAdmin(admin.ModelAdmin):
    list_display = ('izena',)
    prepopulated_fields = {"slug": ("izena",)}

admin.site.register(GamePlaya, GamePlayAdmin)
admin.site.register(Kategoria, KategoriaAdmin)
admin.site.register(Zailtasuna, ZailtasunAdmin)
