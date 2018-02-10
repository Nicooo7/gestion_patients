# coding: utf-8

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from django.template import loader
#from django.core.exceptions import ObjectDoesNotExist


from .models import *
from django.contrib.auth.models import* 
from django.contrib.auth import *
from bs4 import BeautifulSoup
from django.template.response import *
import bs4
import re
import pickle
import os
import json
from nltk import *
from bs4 import BeautifulSoup
from random import *
from unidecode import unidecode
from django.utils.safestring import mark_safe
from.forms import DemandeForm
from django.utils import timezone



app_name = 'gestion_patient'




#_____________________vue_______________________#

def rentrer_patient(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        if form.is_valid(): 
            demande = form.save()
            demande.heure = timezone.now()
            demande.save()
            print("demande sauvegardée")
        else:
            print("formulaire non valide")
        form = DemandeForm()
        return render(request, 'rentrer_patient.html', {'form': form})
                
    else:
        form = DemandeForm()
        
    demandes= Demande.objects.all()    
    return render(request, 'rentrer_patient.html', {'form': form})
   

def afficher_patient(request):
    demandes= Demande.objects.all()
    return render(request, 'afficher_patient.html', {"demandes":demandes})

def supprimer_patient(request):
    id = str(request.GET['id'])
    demande = Demande.objects.get(id=id)
    demande.delete()
    demandes= Demande.objects.all()
    return render(request, 'afficher_patient.html', {"demandes":demandes})

def realisation_patient(request):
    id = str(request.GET['id'])
    demande = Demande.objects.get(id=id)
    
    demande.realisation = "oui"
    demande.save()
    demandes= Demande.objects.all()
    return render(request, 'afficher_patient.html', {"demandes":demandes})























