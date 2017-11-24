# coding: utf-8
from django.conf.urls import url
from django.conf.urls import url, include
from django.views.generic import ListView
from django.views.generic import TemplateView
from gestion_patient import views
from django.contrib import admin




page =[]
liste_des_elements_de_page = []



urlpatterns = [
	
    
   
    url(r'^admin/', admin.site.urls),
    url(r'^rentrer_patient', views.rentrer_patient, name = 'rentrer_patient'),
    url(r'^afficher_patient', views.afficher_patient, name = 'afficher_patient'),
    ]



