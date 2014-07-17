from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from gamerauntsia.gameplaya.models import GamePlaya
from gamerauntsia.berriak.models import Berria

def index(request):
    gameplayak = GamePlaya.objects.filter(publikoa_da=True).order_by('-pub_date')[:4]
    return render_to_response('index.html', locals(),context_instance=RequestContext(request))

def google(request):
    h = {}
    return render_to_response('googleaf6b2cbbb22dca3f.html', h,context_instance=RequestContext(request))

def rating(request):
    value = request.GET.get('value')
    slug = request.GET.get('slug')
    tutoriala = get_object_or_404(GamePlaya,slug=slug)
    if tutoriala:
        tutoriala.botoak += 1
        tutoriala.puntuak += float(value)/2
        tutoriala.save()
    	return HttpResponse('True')
    return HttpResponse('False')