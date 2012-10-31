from django import template
from tutoreus.tutorialak.models import Tutoriala
from tutoreus.berriak.models import Berria

register = template.Library()

@register.inclusion_tag('top_tutorialak.html')
def top_tutorialak():
    h = {}
    h['zerr_tutoriala'] = Tutoriala.objects.filter(publikoa_da=True).order_by('-pub_date')[:10]
    return h
 
@register.inclusion_tag('behe_blokeak.html') 
def azken_berriak():
    h = {}
    h['berriak'] = Berria.objects.all().order_by('-pub_date')[:5]
    return h

