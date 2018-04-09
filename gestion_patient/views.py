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

#_____________________classes_______________________#


class Titre:
    def __init__(self, intitule, optionnel, cl):
        self.optionnel = optionnel
        self.intitule = intitule
        self.cl= cl

class Item:

    liste_des_items= []
    liste_des_titres=[]
    liste_des_intitules_des_titres = []

    def __init__ (self, titre_item, label_element, categorie, formule, defaut, optionnel, cible=""):
        self.titre_item= titre_item
        self.label_element = label_element
        self.formule= formule
        self.categorie = categorie
        self.defaut= defaut
        self.optionnel= optionnel
        self.cible = cible

        for at in self.__dict__.values():
            at = mark_safe(at)

        Item.liste_des_items.append(self)


        #créer un titre de rubrique optionnel
        if self.titre_item not in Item.liste_des_intitules_des_titres:
            t = Titre(intitule=self.titre_item, optionnel=self.optionnel, cl=self.categorie)
            Item.liste_des_intitules_des_titres.append(t.intitule)
            Item.liste_des_titres.append(t)

class CRTYPE:
    def __init__(self, indication, technique, resultat, conclusion):
        self.indication = indication
        self.technique = technique
        self.resultat = resultat
        self.conclusion = conclusion

    def compte_rendu(self):
        CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
        if self.conclusion != "":
            CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
        CRTYPE = mark_safe(CRTYPE)
        return(CRTYPE)


def remise_a_zero_des_items():
    Item.liste_des_items= []
    Item.liste_des_titres=[]
    Item.liste_des_intitules_des_titres = []


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

def radiographies(request):
    class Item:
    
        liste= []

        def __init__ (self, region_anatomique, sous_rubriques, adresseImage):
            self.region_anatomique = mark_safe(region_anatomique)
            
            L= []    
            for r in sous_rubriques:
                L.append(mark_safe(r))
            self.sous_rubriques=L
            self.adresseImage=adresseImage

            Item.liste.append(self)
      
   
    Item(region_anatomique= "thorax" ,sous_rubriques= ["pulmonaire", "grill costal"],adresseImage="images/thorax.png" )        
    Item(region_anatomique= "rachis" ,sous_rubriques= ["rachis lombaire", "rachis dorsal", 'rachis cervical'],adresseImage="")
    Item(region_anatomique= "membres supérieurs" ,sous_rubriques= ["epaule", "bras", "coude", "avant bras","poignet", "main"],adresseImage="" )
    Item(region_anatomique= "membres inférieurs" ,sous_rubriques= ["bassin", "hanches", "cuisse", "genou", "jambe", "cheville"],adresseImage="" )
    Item(region_anatomique= "crane" ,sous_rubriques= ["massif facial", "sinus"],adresseImage="" )

    titre="radiographies"

    return render(request, 'radiographies.html', {"liste": Item.liste, "titre": titre})

def scanner(request):
    class Item:
    
        liste= []

        def __init__ (self, region_anatomique, sous_rubriques, adresseImage):
            self.region_anatomique = mark_safe(region_anatomique)
            
            L= []    
            for r in sous_rubriques:
                L.append(mark_safe(r))
            self.sous_rubriques=L
            self.adresseImage = adresseImage

            Item.liste.append(self)
      
   
    Item(region_anatomique= "encéphale" ,sous_rubriques= ["AVC", "traumatisme", "troubles cognitifs"], adresseImage="" )        
    Item(region_anatomique= "cou" ,sous_rubriques= ["ORL", "rachis"], adresseImage="")
    Item(region_anatomique= "thorax" ,sous_rubriques= ["EP", "PID", "Dissection", "pneumopathie","traumatisme"], adresseImage="images/thorax.png" )
    Item(region_anatomique= "abdomen et pelvis" ,sous_rubriques= ["infection", "douleur",  "oncologie", "autre"], adresseImage="" )
    Item(region_anatomique= "vaisseaux" ,sous_rubriques= ["AOMI", "anévrisme aortique, autre"], adresseImage="" )
    Item(region_anatomique= "membres" ,sous_rubriques= ["traumatisme" , "oncologie"] , adresseImage="")

    titre="scanners"

    return render(request, 'scanner.html', {"liste": Item.liste, "titre": titre})

def radiographie_poumon(request):

    remise_a_zero_des_items()

    c = CRTYPE (  
                                indication="", 
                                technique="radiographie pulmonaire de face", 
                                resultat="Pas d'anomalie notable pulmonaire, pleurale, de la silhouette médiastinale, osseuse, des parties molles périphériques dans le champ d'exploration", 
                                conclusion=""

                                )
    compteRenduType = CRTYPE.compte_rendu(c)

      


    #INDICATIONS:
    Item(titre_item="INDICATION", label_element="dyspnée", categorie="indication", formule="Bilan de dyspnée", defaut= "", optionnel="non", cible="resultat_dyspnee")   
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


    return render(request, 'radiographies_pulmonaire.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_cheville(request):

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="traumatisme", categorie="indication", formule="Bilan post traumatique", defaut= "", optionnel="non", cible="resultat_traumatisme")   
    Item(titre_item="INDICATION", label_element="douleurs non traumatiques", categorie="indication", formule="Douleurs non traumatiques", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="chez un enfant", categorie="indication", formule="chez un enfant de ... ans", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="droite", categorie="indication", formule="de cheville droite", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de cheville gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-traumatisme
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture malléolaire", categorie="resultat_traumatisme", formule="Fracture de la malléole ...", defaut= "Intégrité des malléoles", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture fibulaire", categorie="resultat_traumatisme", formule="Fracture fibulaire", defaut= "intégrité de la fibula", optionnel="oui" ) 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture tibiale", categorie="resultat_traumatisme", formule="Fracture tibiale", defaut= "intégrité du tibia", optionnel="oui" )
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="diastasis talo-crural", categorie="resultat_trauamtisme", formule="Diastasis talo-crural latéral/médial", defaut="Absence de diastasis talo-crural", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture ostéo-chondrale du talus", categorie="resultat_traumatisme", formule="Fracture ostéo-chondrale du talus: ...", defaut= "intégrité du dôme du talus", optionnel="oui" )
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="arrachement osseux 5ème métatarsien", categorie="resultat_traumatisme", formule="Arrachement osseux à l'insertion du 5ème métatarsien", defaut= "pas de signe d'arrachement osseux à l'insersion du tendon du court fibulaire sur la base du 5ème métatarsion", optionnel="oui" )
   


    #RESULTATS_Autres
    Item(titre_item="AUTRES", label_element="anomalie osseuse", categorie="resultat_autre", formule="Anomalie osseuse:", 
    defaut= "pas d'anomalie osseuse", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie articulaire", categorie="resultat_autre", formule="Anomalie articulaire:", 
    defaut= "pas d'anomalie articulaire", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    defaut= "pas d'anomalie de la silhouette médiastinale", optionnel="non")
    Item(titre_item="AUTRES", label_element="corps étranger", categorie="resultat_autre", defaut= "pas de corps étranger radio-opaque", optionnel="non", formule="Corps étranger")
    



    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de cheville D G face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de cheville" 
    page = "radiographie_cheville"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_cheville.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_genou(request):

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="traumatisme", categorie="indication", formule="Bilan post traumatique", defaut= "", optionnel="non", cible="resultat_traumatisme")   
    Item(titre_item="INDICATION", label_element="douleurs non traumatiques", categorie="indication", formule="Douleurs non traumatiques", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="chez un enfant", categorie="indication", formule="chez un enfant de ... ans", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="droite", categorie="indication", formule="de genou droit", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de genou gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-traumatisme
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture de la patella", categorie="resultat_traumatisme", formule="Fracture de la patella", defaut= "Intégrité de la patella", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture du fémur", categorie="resultat_traumatisme", formule="Fracture du fémur", defaut= "intégrité du fémur", optionnel="oui" ) 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture tibiale", categorie="resultat_traumatisme", formule="Fracture du tibia", defaut= "intégrité du tibia", optionnel="oui" )
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture de la fibula", categorie="resultat_traumatisme", formule="fracture de la fibula", defaut="Intégrité de la fibula", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="hématrose", categorie="resultat_traumatisme", formule="hématrose", defaut= "pas d'hématrose", optionnel="oui" )
   


    #RESULTATS_Autres
    Item(titre_item="AUTRES", label_element="anomalie osseuse", categorie="resultat_autre", formule="Anomalie osseuse:", 
    defaut= "pas d'anomalie osseuse", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie articulaire", categorie="resultat_autre", formule="Anomalie articulaire:", 
    defaut= "pas d'anomalie articulaire", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    defaut= "pas d'anomalie de la silhouette médiastinale", optionnel="non")
    Item(titre_item="AUTRES", label_element="corps étranger", categorie="resultat_autre", defaut= "pas de corps étranger radio-opaque", optionnel="non", formule="Corps étranger")
    


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de genou D G face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de genou" 
    page = "radiographie_genou"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  















    return render(request, 'radiographies_cheville.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_coude(request):

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="traumatisme", categorie="indication", formule="Bilan post traumatique", defaut= "", optionnel="non", cible="resultat_traumatisme")   
    Item(titre_item="INDICATION", label_element="douleurs non traumatiques", categorie="indication", formule="Douleurs non traumatiques", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="chez un enfant", categorie="indication", formule="chez un enfant de ... ans", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="droite", categorie="indication", formule="de coude droit", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de coude gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-traumatisme
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture du capitulum", categorie="resultat_traumatisme", formule="Fracture du capitulum", defaut= "Intégrité de la patella", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture du condyle médial", categorie="resultat_traumatisme", formule="Fracture du condyle médial", defaut= "intégrité du condyle médial", optionnel="oui" ) 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture du condyle latéral", categorie="resultat_traumatisme", formule="Fracture du condyle latéral", defaut= "intégrité du condyle latéral", optionnel="oui" )
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture de l'olécrane", categorie="resultat_traumatisme", formule="Fracture de l'olécrane", defaut="Intégrité de l'olécrane", optionnel="oui") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="hématrose", categorie="resultat_traumatisme", formule="hématrose", defaut= "pas d'hématrose", optionnel="oui" )
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="luxation", categorie="resultat_traumatisme", formule="luxation", defaut= "pas de luxation du coude", optionnel="oui" )



    #RESULTATS_Autres
    Item(titre_item="AUTRES", label_element="anomalie osseuse", categorie="resultat_autre", formule="Anomalie osseuse:", 
    defaut= "pas d'anomalie osseuse", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie articulaire", categorie="resultat_autre", formule="Anomalie articulaire:", 
    defaut= "pas d'anomalie articulaire", optionnel="non")
    Item(titre_item="AUTRES", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    defaut= "pas d'anomalie de la silhouette médiastinale", optionnel="non")
    Item(titre_item="AUTRES", label_element="corps étranger", categorie="resultat_autre", defaut= "pas de corps étranger radio-opaque", optionnel="non", formule="Corps étranger")
    



    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du coude D G, face et profil", 
                                resultat="Pas d'hémarthrose.Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du coude" 
    page = "radiographie_coude"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_coude.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_poignet(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de poignet D G face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de poignet" 
    page = "radiographie_poignet"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_poignet.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_epaule(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie d'épaule D G face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie d'épaule" 
    page = "radiographie_epaule"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_epaule.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_rachis_lombaire(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du rachis lombaire, face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du rachis lombaire" 
    page = "radiographie_rachis_lombaire"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_rachis_lombaire.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_rachis_dorsal(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du rachis dorsal, face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du rachis dorsal" 
    page = "radiographie_rachis_dorsal"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_rachis_dorsal.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_rachis_cervical(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du rachis cervical, face et profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du rachis cervical" 
    page = "radiographie_rachis_cervical"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_rachis_cervical.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_main(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de la main D G, face et oblique, centrées sur le X ème rayon", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de la main" 
    page = "radiographie_main"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_main.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_pied(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du pied D G, face et oblique, centrées sur le X ème rayon", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)


    titre = "radiographie du pied" 
    page = "radiographie_pied"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_pied.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})



def radiographie_bassin(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du bassin de face", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du bassin" 
    page = "radiographie_bassin"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_bassin.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_bras(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du bras D G de face et de profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du bras" 
    page = "radiographie_bras"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_bras.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_avant_bras(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de l' avant-bras D G de face et de profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de l'avant-bras" 
    page = "radiographie_avant-bras"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_avant-bras.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_cuisse(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de la cuisse D G de face et de profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de la cuisse" 
    page = "radiographie_cuisse"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_cuisse.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_jambe(request):

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

    class CRTYPE:
        def __init__(self, indication, technique, resultat, conclusion):
            self.indication = indication
            self.technique = technique
            self.resultat = resultat
            self.conclusion = conclusion

        def compte_rendu(self):
            CRTYPE = "INDICATION:"+ "xxxx"+ self.indication + "xxxx" + "TECHNIQUE:" + "xx" + self.technique + "xxxx" + "RESULTAT" + "xx" + self.resultat 
            if self.conclusion != "":
                CRTYPE = CRTYPE +  "xxxx" + "CONCLUSION: " + "xx" + self.conclusion
            CRTYPE = mark_safe(CRTYPE)
            return(CRTYPE)


      
    """

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


    """


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie de la jambe D G de face et de profil", 
                                resultat="Pas de lésion traumatique ostéo-articulaire décelée ni anomalie notable retenue", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie de la jambe" 
    page = "radiographie_jambe"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radiographies_jambe.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})





