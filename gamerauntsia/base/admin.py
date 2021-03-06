from models import Terminoa
from django.contrib import admin


class TerminoaAdmin(admin.ModelAdmin):
    list_display = ('term_eu','term_es','term_en','jokoa')
    search_fields = ['term_eu','term_es','term_en']
    raw_id_fields = ('jokoa',)
    ordering = ('term_eu',)
   

admin.site.register(Terminoa, TerminoaAdmin)
