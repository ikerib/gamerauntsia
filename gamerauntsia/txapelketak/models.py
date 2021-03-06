from django.db import models
from django.conf import settings
from django.db.models import Q
from photologue.models import Photo
from gamerauntsia.gamer.models import GamerUser
from gamerauntsia.jokoa.models import Jokoa
from gamerauntsia.gameplaya.models import GamePlaya
from datetime import datetime
from django.template import defaultfilters as filters
from mptt.models import MPTTModel, TreeForeignKey
from django.template.loader import get_template
from django.template import Context
from django.db.models.signals import post_save

MOTA = (
    ('0','Kanporaketa'),
    ('1','Liga'),
    ('2','Konbinatua'),
)

MODALITATEA = (
    ('0','Bakarka'),
    ('1','Taldeka'),
)

EGOERA = (
    ('0','Izen ematea zabalik'),
    ('1','Partidak sortzen'),
    ('2','Txapelketa jokuan'),
    ('3','Bukatuta'),
)

class Txapelketa(models.Model):
    izena = models.CharField(max_length=64)
    slug = models.SlugField(db_index=True, unique=True, help_text="Eremu honetan kategoria honen URL helbidea zehazten ari zara.")
    desk = models.TextField(max_length=256,null=True,blank=True)
    arauak = models.TextField(max_length=256,null=True,blank=True)
    saria = models.TextField(max_length=256,null=True,blank=True)
    irudia = models.ForeignKey(Photo,null=True,blank=True)
    mota = models.CharField(max_length=1, choices=MOTA, default='0')
    modalitatea = models.CharField(max_length=1, choices=MODALITATEA, default='0')
    status = models.CharField(max_length=1, choices=EGOERA, default='0')
    live_bideoa = models.CharField(max_length=100,null=True,blank=True, help_text="Eremu honetan bideoaren URL kodea itsatsi behar duzu. Adb.: c21XAuI3aMo")
    hashtag = models.CharField(max_length=100,null=True,blank=True)

    jokalariak = models.ManyToManyField(GamerUser,related_name="jokalariak",verbose_name="Inskripzioa",null=True,blank=True)

    jokoa = models.ForeignKey(Jokoa)
    adminak = models.ManyToManyField(GamerUser,related_name="adminak",verbose_name="Egileak")

    irabazi = models.IntegerField('Puntuak irabaztean', default=0)
    galdu = models.IntegerField('Puntuak galtzean', default=0)
    berdinketa = models.IntegerField('Puntuak berdinketan', default=0)

    publikoa_da = models.BooleanField(default=True)
    pub_date = models.DateTimeField('Publikazio data', default=datetime.now)
    insk_date = models.DateTimeField('Izen ematea', default=datetime.now)
    shared = models.BooleanField(default=False)

    def get_jokalariak(self):
        return self.jokalariak.all()

    def jokalariak_count(self):
        return self.get_jokalariak().count()

    def get_single_gamers(self):
        singles = []
        gamers = self.get_jokalariak()
        teams = self.get_partaideak()
        for gamer in gamers:
            has_team = False
            for team in teams:
                if gamer in team.jokalariak.all():
                    has_team = True
                if has_team:
                    break
            if not has_team:
                singles.append(gamer)
        return singles

    def get_partaideak(self,order=None):
        if order:
            return Partaidea.objects.filter(txapelketa=self).order_by(*order)
        return Partaidea.objects.filter(txapelketa=self)

    def partaideak_count(self):
        return self.get_partaideak().count()

    def get_partidak(self):
        return Partida.objects.filter(txapelketa=self).order_by('date')

    def get_desk_txikia(self):
        if len(self.desk) > 150:
            return filters.striptags(self.desk)[:150]+'...'
        return filters.striptags(self.desk)

    def get_next_match(self):
        matches = self.partida_set.filter(Q(emaitza__isnull=True)|Q(emaitza__iexact='')).order_by("-date")
        if matches:
            return matches[0].date
        return None

    def get_desk_index(self):
        if len(self.desk) > 400:
            return filters.striptags(self.desk)[:400]+'...'
        return filters.striptags(self.desk)

    def get_absolute_url(self):
        return '%stxapelketak/%s' % (settings.HOST, self.slug)

    def getTwitText(self):
        if self.erabiltzailea.twitter_id:
            return self.izena + ' ' + self.get_absolute_url() + ' @%s 2dz' % (self.erabiltzailea.twitter_id)
        else:
            return self.izena + ' ' + self.get_absolute_url()

    def getEmailText(self):
       htmly = get_template('buletina/buletina.html')
       plaintext = get_template('buletina/buletina.txt')
       d = Context(
           {
               'izenburua': self.izena,
               'deskribapena': self.get_desk_txikia(),
               'url': self.get_absolute_url(),
               'img_url': settings.HOST + self.irudia.get_blog_url()
           }
       )
       subject = settings.EMAIL_SUBJECT + ' ' + self.izena
       text_content = plaintext.render(d)
       html_content = htmly.render(d)
       return subject, text_content, html_content

    def getFBinfo(self):
        return self.izena, self.desk, self.irudia

    class Meta:
        verbose_name = "Txapelketa"
        verbose_name_plural = "Txapelketak"

    def __unicode__(self):
        return u'%s' % (self.izena)

class Partaidea(models.Model):
    izena = models.CharField(max_length=64,null=True,blank=True)
    irudia = models.ForeignKey(Photo,null=True,blank=True)

    txapelketa = models.ForeignKey(Txapelketa)
    irabazlea = models.BooleanField(default=False)
    jokalariak = models.ManyToManyField(GamerUser,null=True,blank=True)

    win = models.IntegerField('Irabazitakoak', default=0)
    lose = models.IntegerField('Galdutakoak', default=0)
    draw = models.IntegerField('Berdindutakoak', default=0)
    matches = models.IntegerField('Jokatutakoak', default=0)
    points = models.IntegerField('Puntuak', default=0)

    def is_group(self):
        if len(self.jokalariak.all()) > 1:
            return True
        return False
        
    def get_absolute_url(self):
        if self.is_group():
            return None
        else:
            return "%s" % (self.jokalariak.all()[0].get_absolute_url())

    def get_photo(self):
        if self.is_group():
            if self.irudia:
                return self.irudia
            else:
                try:
                    return Photo.objects.get(slug=GROUP_PHOTO_SLUG)
                except:
                    return None
        else:
            return self.jokalariak.all()[0].get_photo()

    def get_izena(self):
        if not self.izena:
            if not self.jokalariak.all():
                return u'%s' %(self.izena)
            elif not self.is_group:
                return u'%s' % (self.jokalariak.all()[0].getFullName())
            else:
                return u'%s' % (", ".join([p.getFullName() for p in self.jokalariak.all()]))
        return u'%s' %(self.izena)

    class Meta:
        verbose_name = "Partaidea"
        verbose_name_plural = "Partaideak"

    def __unicode__(self):
        return self.get_izena()

class Partida(MPTTModel):
    partaideak = models.ManyToManyField(Partaidea,null=True,blank=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    jardunaldia = models.IntegerField('Jardunaldia', default=1)
    emaitza = models.CharField(max_length=50,null=True,blank=True)

    txapelketa = models.ForeignKey(Txapelketa)
    gameplaya = models.ForeignKey(GamePlaya,null=True,blank=True)
    date = models.DateTimeField('Data', null=True,blank=True)

    def get_izena(self):
        if self.partaideak.all():
            return " VS ".join([p.get_izena() for p in self.partaideak.all()])
        else:
            return u'%d jardunaldia' % (self.jardunaldia)

    def get_partaide_list(self):
        if self.partaideak.all():
            return " VS ".join([p.get_izena() for p in self.partaideak.all()])
        else:
            return u'???'

    class MPTTMeta:
        order_insertion_by = ['jardunaldia']

    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidak"

    def __unicode__(self):
        return u'%s' % (self.get_izena())


def update_classification(sender,instance,**kwargs):
    if not kwargs['created']:
        if instance.emaitza:
            for parta in instance.partaideak.all():
                irabazi = 0
                galdu = 0
                berdindu = 0
                jokatuta = 0
                partidak = Partida.objects.filter(txapelketa=instance.txapelketa,partaideak=parta,emaitza__isnull=False).exclude(emaitza__exact="").order_by("date")
                for parti in partidak:
                    emaitza = parti.emaitza.split("-")
                    e1 = emaitza[0].strip()
                    e2 = emaitza[1].strip()
                    etxeko = parti.partaideak.all()[0]
                    if e1 > e2:
                        if etxeko == parta:
                            irabazi += 1
                        else:
                            galdu += 1
                    if e1 < e2:
                        if etxeko == parta:
                            galdu += 1
                        else:
                            irabazi += 1
                    if e1 == e2:
                        berdindu += 1
                    jokatuta += 1
                ##PUNTUAKETA
                parta.win = irabazi
                parta.lose = galdu
                parta.draw = berdindu
                parta.points = irabazi * instance.txapelketa.irabazi + galdu * instance.txapelketa.galdu + berdindu * instance.txapelketa.berdinketa
                parta.matches = jokatuta
                parta.save()

post_save.connect(update_classification, sender=Partida)
