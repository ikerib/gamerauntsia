from django.db import models
from django.conf import settings
from photologue.models import Photo
from gamerauntsia.jokoa.models import Jokoa, Plataforma
from gamerauntsia.gamer.models import GamerUser
from datetime import datetime
from django.template import defaultfilters as filters
from django.template.loader import get_template
from django.template import Context

STATUS = (
    ('0','Zirriborroa'),
    ('1','Publikoa'),
)

class Kategoria(models.Model):
    izena = models.CharField(max_length=64)
    slug = models.SlugField(db_index=True, unique=True, help_text="Eremu honetan kategoria honen URL helbidea zehazten ari zara.")
    desk = models.TextField(max_length=256,null=True,blank=True)
    irudia = models.ForeignKey(Photo,null=True,blank=True)

    class Meta:
        verbose_name = "Kategoria"
        verbose_name_plural = "Kategoriak"

    def __unicode__(self):
        return u'%s' % (self.izena)

class Zailtasuna(models.Model):
    izena = models.CharField(max_length=64)
    slug = models.SlugField(db_index=True, unique=True, help_text="Eremu honetan zailtasun honen URL helbidea zehazten ari zara.")

    class Meta:
        verbose_name = "zailtasuna"
        verbose_name_plural = "zailtasunak"

    def __unicode__(self):
        return u'%s' % (self.izena)

class GamePlaya(models.Model):
    izenburua = models.CharField(max_length=64)
    slug = models.SlugField(unique=True,db_index=True, help_text="Eremu honetan game play honen URL helbidea zehazten ari zara.")
    desk = models.TextField(max_length=256)
    iraupena_min = models.IntegerField(max_length=2,default=0)
    iraupena_seg = models.IntegerField(max_length=2, null=False,blank=False,default=0)

    argazkia = models.ForeignKey(Photo)
    bideoa = models.CharField(max_length=100,null=True,blank=True,help_text="Eremu honetan Youtube bideoaren URL kodea itsatsi behar duzu. Adb.: c21XAuI3aMo")

    jokoa = models.ForeignKey(Jokoa, related_name='gameplay')
    plataforma = models.ForeignKey(Plataforma, related_name='gameplay')
    zailtasuna = models.ForeignKey(Zailtasuna, related_name='gameplay')
    kategoria = models.ManyToManyField(Kategoria, related_name='gameplay')

    erabiltzailea = models.ForeignKey(GamerUser,related_name='gameplayak')
    publikoa_da = models.BooleanField(default=False, verbose_name="Publikatzeko prest")
    pub_date = models.DateTimeField('publikazio data', default=datetime.now)
    mod_date = models.DateTimeField('modifikazio data', default=datetime.now)
    status = models.CharField(max_length=1, choices=STATUS, default='0')
    shared = models.BooleanField(default=False, help_text="Lauki hau automatikoki markatuko da sistemak edukia sare sozialetan elkarbanatzean.")

    def get_desk_index(self):
    	if len(self.desk) > 400:
    	    return filters.striptags(self.desk)[:400]+'...'
        return filters.striptags(self.desk)

    def get_desk_txikia(self):
    	if len(self.desk) > 150:
    	    return filters.striptags(self.desk)[:150]+'...'
        return filters.striptags(self.desk)

    def get_puntuak(self):
        if self.puntuak == 0:
            return 0
        return round(self.puntuak/self.botoak, .5)

    def get_rating(self):
        return int(self.get_puntuak()*2)

    def get_url(self):
        url = ''
        if self.bideoa.startswith('http://vimeo.com'):
            url = self.bideoa.replace('http://vimeo.com/','')
        elif self.bideoa.startswith('http://youtu.be'):
            url = self.bideoa.replace('http://youtu.be/','')
    	return url

    def get_absolute_url(self):
        return '%sgameplayak/%s' % (settings.HOST, self.slug)

    def getTwitText(self):
        if self.erabiltzailea.twitter_id:
            return self.izenburua + ' ' + self.get_absolute_url() + ' @%s 2dz' % (self.erabiltzailea.twitter_id)
        else:
            return self.izenburua + ' ' + self.get_absolute_url()

    def getEmailText(self):
       htmly = get_template('buletina/buletina.html')
       plaintext = get_template('buletina/buletina.txt')
       d = Context(
           {
               'izenburua': self.izenburua,
               'deskribapena': self.get_desk_txikia(),
               'url': self.get_absolute_url(),
               'img_url': settings.HOST + self.argazkia.get_blog_url()
           }
       )
       subject = settings.EMAIL_SUBJECT + ' ' + self.izenburua
       text_content = plaintext.render(d)
       html_content = htmly.render(d)
       return subject, text_content, html_content

    def getFBinfo(self):
        return self.izenburua, self.desk, self.argazkia

    def save(self, *args, **kwargs):
        if not self.izenburua[0].isupper():
            self.izenburua[0].upper()
        if not self.desk[0].isupper():
            self.desk[0].upper()
        super(GamePlaya,self).save(*args,**kwargs)

    class Meta:
        verbose_name = "gameplaya"
        verbose_name_plural = "gameplayak"

    def __unicode__(self):
        return u'%s' % (self.izenburua)
