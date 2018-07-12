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

     #RADIO
     url(r'radiographies/$', views.radiographies, name = 'radiographies'),
     url(r'radiographies/pulmonaire/$', views.radiographie_poumon, name = 'radiographies_pulmonaire'),
     url(r'radiographies/cheville/$', views.radiographie_cheville, name = 'radiographies_cheville'),
     url(r'radiographies/epaule/$', views.radiographie_epaule, name = 'radiographies_epaule'),
     url(r'radiographies/genou/$', views.radiographie_genou, name = 'radiographies_genou'),
     url(r'radiographies/poignet/$', views.radiographie_poignet, name = 'radiographies_poignet'),
     url(r'radiographies/coude/$', views.radiographie_coude, name = 'radiographies_coude'),
     url(r'radiographies/pied/$', views.radiographie_pied, name = 'radiographies_pied'),
     url(r'radiographies/main/$', views.radiographie_main, name = 'radiographies_main'),
     url(r'radiographies/bassin/$', views.radiographie_bassin, name = 'radiographies_bassin'),
     url(r'radiographies/rachis lombaire/$', views.radiographie_rachis_lombaire, name = 'radiographies_rachis_lombaire'),
     url(r'radiographies/rachis dorsal/$', views.radiographie_rachis_dorsal, name = 'radiographies_rachis_dorsal'),
     url(r'radiographies/rachis cervical/$', views.radiographie_rachis_cervical, name = 'radiographies_rachis_cervical'),
     url(r'radiographies/bras/$', views.radiographie_bras, name = 'radiographies_bras'),
     url(r'radiographies/jambe/$', views.radiographie_jambe, name = 'radiographies_jambe'),
     url(r'radiographies/avant_bras/$', views.radiographie_avant_bras, name = 'radiographies_avant_bras'),
     url(r'radiographies/cuisse/$', views.radiographie_cuisse, name = 'radiographies_cuisse'),

     #IRM
     url(r'irm/$', views.irm, name = 'irm'),
     url(r'irm/cardiaque/$', views.irm_cardiaque, name = 'irm_cardiaque'),
     url(r'irm/prostate/$', views.irm_prostate, name = 'irm_prostate'),
     url(r'irm/cerebrale/$', views.irm_cerebrale, name = 'irm_cerebrale'),
     url(r'irm/foie/$', views.irm_foie, name = 'irm_foie'),
     url(r'irm/genou/$', views.irm_genou, name = 'irm_genou'),
     url(r'irm/rachis_lombaire/$', views.irm_rachis_lombaire, name = 'irm_rachis_lombaire'),


     url(r'commandeVocale/$', views.commandeVocale, name = 'commandeVocale'),

     url(r'^accueil', views.accueil, name = 'accueil'),
    ]



