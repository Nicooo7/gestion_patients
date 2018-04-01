# coding: utf-8
from django.conf.urls import url
from django.conf.urls import url, include
from django.views.generic import ListView
from django.views.generic import TemplateView
from gestion_patient import views
from django.contrib import admin
from django.conf.urls import url, include
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static




page =[]
liste_des_elements_de_page = []



urlpatterns = [
	
    
   
    url(r'^admin/', admin.site.urls),
    url(r'^rentrer_patient', views.rentrer_patient, name = 'rentrer_patient'),
    url(r'^afficher_patient', views.afficher_patient, name = 'afficher_patient'),
     url(r'^supprimer_patient', views.supprimer_patient, name = 'afficher_patient'),
     url(r'^realisation_patient', views.realisation_patient, name = 'afficher_patient'),

#____________________________________________CR type________________________________

     url(r'^scanner', views.scanner, name = 'scanner'),
     #url(r'^radiographie', views.radiographie, name = 'radiographie'),
     url(r'^radiographie_poumon', views.radiographie_poumon, name = 'radiographie_poumon'),
     url(r'^accueil', views.accueil, name = 'accueil'),
    ]



