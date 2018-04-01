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



#__________________CR type__________________#

def accueil(request):
    class Datas:
        def __init__ (self):
            self.rubriques =["scanner", "echographie", "radiographie", "irm", "gestion_patients"]
      
    datas = Datas()      
    return render(request, 'accueil.html', {"datas": datas})

def scanner(request):
    class Datas:
        def __init__ (self):
            self.page = "radiographie"
            self.regions_anatomiques =["encéphale", "cou","thorax", "abdomen et pelvis", "vaisseaux", "membres"]
            self.thorax_titres =["EP", "PID", "dissection"]
      
    datas = Datas()      
    return render(request, 'scanner.html', {"datas": datas})

"""def radiographie(request):
    print("radiographie")
    class Datas:
        def __init__ (self):
            self.page = "radiographie"
            self.regions_anatomiques =["tête", "rachis","thorax", "abdomen", "membre superieur", "membre inférieur"]
            self.thorax_titres =["poumon", "grille costal"]
      
    datas = Datas 
    page = "radiographie"
    titre = "radiographie"      
    return render(request, 'radiographie.html', {"datas": datas, "page":page, "titre":titre})"""

def radiographie_poumon(request):

    class Titre:
        def __init__(self, intitule, optionnel, cl):
            self.optionnel = optionnel
            self.intitule = intitule
            self.cl= cl

    class Item:

        liste_des_items= []
        liste_des_titres=[]
        liste_des_intitules_des_titres = []

        def __init__ (self, titre_item, label_element, categorie, formule, defaut, optionnel):
            self.titre_item= titre_item
            self.label_element = label_element
            self.formule= formule
            self.categorie = categorie
            self.defaut= defaut
            self.optionnel= optionnel

            for at in self.__dict__.values():
                at = mark_safe(at)

            Item.liste_des_items.append(self)

            if self.titre_item not in Item.liste_des_intitules_des_titres:
                t = Titre(intitule=self.titre_item, optionnel=self.optionnel, cl=self.titre_item.replace(" ","_"))
                Item.liste_des_intitules_des_titres.append(t.intitule)
                Item.liste_des_titres.append(t)


            
    #INDICATIONS:
    Item(titre_item="INDICATION", label_element="dyspnée", categorie="indication", formule="Bilan de dyspnée", defaut= "", optionnel="non")   
    Item(titre_item="INDICATION", label_element="douleur thoracique", categorie="indication", formule="Douleurs thoraciques", defaut= "", optionnel="non") 
    Item(titre_item="INDICATION", label_element="traumatisme", categorie="indication", formule="bilan post-traumatique", defaut= "", optionnel="non")      
    Item(titre_item="INDICATION", label_element="syndrome infectieux", categorie="indication", formule="Bilan dans un context de syndrome infectieux", defaut= "", optionnel="non") 


    #TECHNIQUE:
    #base
    Item(titre_item="TECHNIQUE", label_element="avec profile", categorie="technique", formule="Radiographie thoracique de face et de profile", defaut= "Radiographie thoracique de face", optionnel="non") 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mal inspiré", categorie="technique", formule=": examen mal inspiré", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="position couchée", categorie="technique", formule=": examen réalisé en position couchée", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="position assise", categorie="technique", formule=": examen réalisé en position assise", defaut= "", optionnel="non") 


    #RESULTAT-Dyspnee
    Item(titre_item="ELEMENTS SPECIFIQUES DE DYSPNEE", label_element="pneumothorax", categorie="resultat_dyspnee", formule="pneumothorax d'abondance ...", defaut= "Pas de pneumothorax", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE DYSPNEE", label_element="epanchement pleural", categorie="resultat_dyspnee", formule="Epanchement pleural ... d'abondance ...", defaut= "Pas d'épanchement pleural", optionnel="oui" ) 
    Item(titre_item="ELEMENTS SPECIFIQUES DE DYSPNEE", label_element="foyer infectieux", categorie="resultat_dyspnee", formule="Opacité en projection ... compatible avec un foyer de pneumonie", defaut="Pas de foyer infectieux", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE DYSPNEE", label_element="opacité", categorie="resultat_dyspnee", formule="lésion focalisée à type de ... située ...", defaut= "Pas d'anomalie focalisée", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE DYSPNEE", label_element="anomalie interstitielle", categorie="resultat_dyspnee", formule="", defaut= "Pas d'anomalie intersititielle patente", optionnel="oui") 


    #RESULTATS_Autres
    Item(titre_item="AUTRES", label_element="anomalie pleurale", categorie="resultat_autre", formule="anomalie pleurale:", 
    defaut= "pas d'anomalie pleurale", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie pulmonaire", categorie="resultat_autre", formule="anomalie pulmonaire:", 
    defaut= "pas d'anomalie pulmonaire", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie du médiastin", categorie="resultat_autre", formule="anomalie de la silhouette médiastinale: ...", 
    defaut= "pas d'anomalie de la silhouette médiastinale", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie osseuse", categorie="resultat_autre", formule="anomalie osseuse ...", 
    defaut= "pas d'anomalie osseuse", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie des parties molles", categorie="resultat_autre", formule="anomalie des parties polles: ...", 
    defaut= "pas d'anomalie des parties molles périphériques", optionnel="non")




    titre = "radiographie pulmonaire" 
    page = "radiographie_poumon"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  

    return render(request, 'radiographie_poumon.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres})























