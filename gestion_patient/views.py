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

    def __init__ (self, titre_item, label_element, categorie, formule, defaut, optionnel, cible="", dialog="", mini="", maxi="",tooltip="", calcul=""):
        self.titre_item= titre_item
        self.label_element = label_element
        self.formule= formule
        self.categorie = categorie
        if tooltip != "":
            self.categorie = self.categorie + tooltip
        self.tooltip = tooltip
        if self.tooltip == "":
            self.tooltip = "vide"
        self.defaut= defaut
        self.optionnel= optionnel
        self.cible = cible
        self.dialog = dialog
        self.min = mini
        self.max = maxi
        if self.min != "":
            self.moy = (self.min + self.max)/2



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

class Select:
    def __init__(self, titre, listeOption, tooltip="", defaut=""):
        self.titre=titre
        self.listeOption=listeOption
        self.tooltip=tooltip
        self.defaut=defaut

class Carte:
    def __init__(self, titre, listeCase=[], listeSelect=[], calcul="vide", listeLesion = [], listeRange=[]):
        self.titre=titre
        self.listeCase = listeCase
        self.listeSelect = listeSelect
        self.listeRange = listeRange
        self.calcul = calcul
        self.listeLesion = listeLesion

class Etape:
    def __init__(self, question, oui=[], non=[], passer=[], ouiCible = [], nonCible = [], cible="", widget="aucun", titre="", premiere=""):
        self.question= question
        self.oui = oui
        self.non = non
        self.ouiCible = ouiCible
        self.nonCible = nonCible
        self.passer = passer
        self.widget = widget
        self.titre= titre
        self.premiere = premiere
        

class Guide:
    def __init__(self, etapes):
        self.etapes= etapes
        
        
def commandeVocale(request):
    return render(request, 'html/commandeVocale.html')

def remise_a_zero_des_items():
    Item.liste_des_items= []
    Item.liste_des_titres=[]
    Item.liste_des_intitules_des_titres = []


#______________________________CARTES_____________________________________


def carteNodulePulmonaire():
   
    item1 = Item(titre_item="noduleLateralite", label_element="gauche", categorie="resultat", formule="gauche", defaut= "", optionnel="non", cible="")  
    item2 = Item(titre_item="noduleLateralite", label_element="droite", categorie="resultat", formule="droit", defaut= "", optionnel="non", cible="")
    select1 = Select(titre=laterlite, listeOption= [item1,item2])


    item1 = Item(titre_item="noduleContours", label_element="spiculé", categorie="resultat", formule="aux contours spiculés", defaut= "", 
    optionnel="non", cible="") 
    item2 = Item(titre_item="noduleContours", label_element="flous", categorie="resultat", formule="aux contours flous", defaut= "", 
    optionnel="non", cible="")
    item3 = Item(titre_item="noduleContours", label_element="réguliers", categorie="resultat", formule="aux contours réguliers", defaut= "", 
    optionnel="non", cible="")
    Select2 = Select(titre=contours, listeOption=[item1, item2,item3])


    item1 = Item(titre_item="noduleSituation", label_element="lobe supérieur", categorie="resultat", formule="localisé au lobe supérieur", defaut="", optionnel="non", cible="") 
    item2 = Item(titre_item="noduleSituation", label_element="lobe moyen", categorie="resultat", formule="localisé au lobe moyen", defaut="", optionnel="non", cible="")
    item3 = Item(titre_item="noduleSituation", label_element="lobe inférieur", categorie="resultat", formule="localisé au lobe inférieur", defaut="", optionnel="non", cible="")
    Select3 = Select(titre=contours, listeOption=[item1, item2,item3])


    carte1 = Carte(titre = "nodule pulmonaire", listeCase= "", listeSelect = [select1, Select2, select3])

    return carte1

def carteFracture():
    
    #orientation
    item1 = Item(titre_item="fracture orientation", label_element="transverse oblique", categorie="", formule="orientation : transverse oblique", defaut= "", optionnel="non", cible="")   
    item2 = Item(titre_item="fracture orientation", label_element="sagittale oblique", categorie="", formule="orientation : sagittal oblique", defaut= "", optionnel="non", cible="")
    item3 = Item(titre_item="fracture orientation", label_element="coronale oblique", categorie="", formule="orientation : coronal oblique", defaut= "", optionnel="non", cible="")
    item3 = Item(titre_item="fracture orientation", label_element="complexe", categorie="", formule="orientation : complexe", defaut= "", optionnel="non", cible="")
    
    select1 = Select(titre="orientation", listeOption=[item1,item2,item3])

    #déplacement
    item1 = Item(titre_item="non déplacée", label_element="non déplacée", categorie="", formule="déplacement : non", defaut= "", optionnel="non", cible="")   
    item2 = Item(titre_item="peu déplacée", label_element="peu déplacée", categorie="", formule="déplacement : peu déplacé", defaut= "", optionnel="non", cible="")   
    item3 = Item(titre_item=" déplacée", label_element="déplacée", categorie="", formule="déplacement : X mm", defaut= "", optionnel="non", cible="")   
    select2 = Select(titre="déplacement", listeOption=[item1,item2,item3])

    #articulaire
    item1 = Item(titre_item="articulaire", label_element="articulaire", categorie="", formule="articulaire", defaut= "non articulaire", optionnel="non", cible="")   

    listeCase =[item1]

    carte1 = Carte(titre = "fracture", listeCase= listeCase, listeSelect = [select1, select2])
    return carte1    

def carteAnomalieCinetiqueCardiaque():
    
    #orientation
    item1 = Item(titre_item="modérée", label_element=" hypokinésie modérée", categorie="", formule="hypokinésie modérée", defaut= "", optionnel="non", cible="")   
    item2 = Item(titre_item="sévère", label_element="hypokinésie sévère", categorie="", formule="hypokinésie sévère", defaut= "", optionnel="non", cible="")
    item3 = Item(titre_item="akinésie", label_element="akinésie", categorie="", formule="akinésie", defaut= "", optionnel="non", cible="")
    
    select1 = Select(titre="cinétique", listeOption=[item1,item2,item3])

    #déplacement
    item1 = Item(titre_item="paroi antérieure", label_element="paroi antérieure", categorie="", formule="intéressant la paroi antérieure", defaut= "", optionnel="non", cible="")   
    item2 = Item(titre_item="paroi inférieure", label_element="paroi inférieure", categorie="", formule="intéressant la paroi inférieure", defaut= "", optionnel="non", cible="")   
    item3 = Item(titre_item="paroi latérale", label_element="paroi latérale", categorie="", formule="intéressant la paroi latérale", defaut= "", optionnel="non", cible="")   
    select2 = Select(titre="localisation", listeOption=[item1,item2,item3])

    #articulaire
    #item1 = Item(titre_item="articulaire", label_element="articulaire", categorie="", formule="articulaire", defaut= "non articulaire", optionnel="non", cible="")   

    listeCase =[item1]

    carte1 = Carte(titre = "anomalieCinetiqueCardiaque", listeCase= listeCase, listeSelect = [select1, select2])
    return carte1    

def carteIndicationProstate():
    
    #___________________ saisie de nombre: range_____________
        item1 = Item(titre_item="PSA", label_element=" Taux de PSA (ng/mL)", categorie="", formule="Taux de PSA (ng/mL): ", defaut= "", optionnel="non", cible="", mini=0, maxi=100)   
        item2 = Item(titre_item="PSA", label_element=" Rapport PSA (%)", categorie="", formule="Rapport de PSA(%): ", defaut= "", optionnel="non", cible="", mini=0, maxi=100,)   

        listeRange= [item1, item2]

    #_________________SELECT__________________

        #Select1
        item1 = Item(titre_item="Risque élevé", label_element="Risque élevé", categorie="", formule="Risque selon la classification D'Amico: élevé", defaut= "", optionnel="non", cible="", )   
        item2 = Item(titre_item="Risque intermédiaire", label_element="Risque intermédiaire", categorie="Risque intermédiaire", formule="Risque selon la classification D'Amico: intermédiaire", defaut= "", optionnel="non", cible="")
        item3 = Item(titre_item="Risque faible", label_element="Risque faible", categorie="", formule="Risque selon la classification D'Amico: faible", defaut= "", optionnel="non", cible="")
        select1 = Select(titre="D'Amico", listeOption=[item1,item2,item3], tooltip="CLASSIFICATION DE D'AMICO:<br><br><br>Risque élevé si Gleason>7, PSA>20, T2c<br><br><br>Risque intermédiaire<br><br><br>Risque faible si Gleason <= 6 et moins de 33 pourcent de biospies positives et PSA<=10 ")


        #liste
        listeSelect= [select1]

    #______________________Cases à cocher
        #item1 = Item(titre_item="articulaire", label_element="articulaire", categorie="", formule="articulaire", defaut= "non articulaire", optionnel="non", cible="")   
        listeCase =[]


    #_________________Finalisation_____
        
        carte1 = Carte(titre = "indicationProstate", listeCase= listeCase, listeSelect = listeSelect, listeRange = listeRange)
        return carte1    

    #____________________________________________________________________________________________________
    #_____________________VUES_____________________________________________________________________________

def carteCalculVolume():
    
    #____________________________calcul volume____________________________________
        item1 = Item(titre_item="D1", label_element=" D1", categorie="", formule="diamètre 1 (mm)", defaut= "", optionnel="non", cible="", mini=0, maxi=50)   
        item2 = Item(titre_item="D2", label_element=" D2", categorie="", formule="diamètre 2 (mm)", defaut= "", optionnel="non", cible="", mini=0, maxi=50,)   
        item3 = Item(titre_item="D3", label_element=" D3", categorie="", formule="diamètre 3 (mm)", defaut= "", optionnel="non", cible="", mini=0, maxi=50)   


        listeRange= [item1, item2, item3]

    #_________________SELECT__________________


        #liste
        listeSelect= []

    #______________________Cases à cocher
        #item1 = Item(titre_item="articulaire", label_element="articulaire", categorie="", formule="articulaire", defaut= "non articulaire", optionnel="non", cible="")   
        listeCase =[]


    #_________________Finalisation_____
        
        carte1 = Carte(titre = "volumeProstate", listeCase= listeCase, listeSelect = listeSelect, listeRange = listeRange, calcul="volume")
        return carte1    

    #____________________________________________________________________________________________________
    #_____________________VUES_____________________________________________________________________________

def carteProstateLesion():
    
    #___________________ saisie de nombre: range_____________
        item1 = Item(titre_item="taille", label_element=" Taille (mm)", categorie="", formule="Taille (mm): ", defaut= "", optionnel="non", cible="", mini=0, maxi=20, tooltip="COMMENT EFFECTUER LA MESURE:<br><br><br> si lésion en zone périphérique: mesurer sur la cartographie ADC <br><br> si dans la zone transitionnelle, mesurer sur la séquence T2")   

        listeRange= [item1]

    #_________________SELECT__________________

        #Select1
        item1 = Item(titre_item="score 1", label_element="signal uniformément hyperintense (normal)", categorie="", formule=1, defaut= "", optionnel="non", cible="", )   
        item2 = Item(titre_item="score 2", label_element="hypo-intensité floue non nodulaire", categorie="", formule=2, defaut= "", optionnel="non", cible="", )   
        item3 = Item(titre_item="score 3", label_element="nodule hétérogène sans hyposignal", categorie="", formule=3, defaut= "", optionnel="non", cible="", )   
        item4 = Item(titre_item="score 4", label_element="nodule bien limité en hyposignal < 1.5 cm", categorie="", formule=4, defaut= "", optionnel="non", cible="", )   
        item5 = Item(titre_item="score 5", label_element="nodule infiltrant ou > 1.5 cm", categorie="", formule=5, defaut= "", optionnel="non", cible="", )   

        select1 = Select(titre="T2", listeOption=[item1,item2,item3, item4, item5])

        
        #Select2
        item1 = Item(titre_item="score 1", label_element="signal homogène (normal)", categorie="", formule=1, defaut= "", optionnel="non", cible="", )   
        item2 = Item(titre_item="score 2", label_element="ADC à la limite de l'hypo-intense (cartographie)", categorie="", formule=2, defaut= "", optionnel="non", cible="", )   
        item3 = Item(titre_item="score 3", label_element="anomalie focale en faible restriction de diffusion", categorie="", formule=3, defaut= "anomalie focale en faible restriction de diffusion", optionnel="non", cible="", )   
        item4 = Item(titre_item="score 4", label_element="anomalie focale en forte restriction de diffusion <1.5 cm", categorie="", formule=4, defaut= "", optionnel="non", cible="", )   
        item5 = Item(titre_item="score 5", label_element="anomalie en forte restriction de diffusion > 1.5 cm", categorie="", formule=5, defaut= "", optionnel="non", cible="", )   

        select2 = Select(titre="diffusion", listeOption=[item1,item2,item3, item4, item5])

        #Select3
        item1 = Item(titre_item="gauche", label_element="gauche", categorie="", formule="gauche", defaut= "", optionnel="non", cible="", )   
        item2 = Item(titre_item="droite", label_element="droite", categorie="", formule="droite", defaut= "", optionnel="non", cible="", )   
        
        select3 = Select(titre="latéralisation", listeOption=[item1,item2,item3])

        #select4
        item1 = Item(titre_item="périphérique", label_element="périphérique", categorie="", formule="en zone périphérique", defaut= "", optionnel="non", cible="", )   
        item2 = Item(titre_item="transitionnelle", label_element="transitionnelle", categorie="", formule="en zone transitionnelle", defaut= "", optionnel="non", cible="", )   
        
        select4 = Select(titre="zone", listeOption=[item1,item2,item3])


        #liste
        listeSelect= [select1, select2, select3, select4]
        for select in listeSelect:
            select.tooltip = select.titre



    #______________________Cases à cocher
        item1 = Item(titre_item="lésion focalisée", label_element="lésion focalisée", categorie="", formule="Lésion focalisée en hyposignal T2 située au niveau de la zone périphérique", defaut= "non articulaire", optionnel="non", cible="")   
        listeCase =[]



    #_________________Finalisation_____
        
        listeLesion= ["lésion1", "lésion2", "lésion3", "lésion4", "lésion5"]

        carte1 = Carte(titre = "prostateLesion", listeCase= listeCase, listeSelect = listeSelect, listeRange = listeRange, listeLesion=listeLesion, calcul="pirads")
        return carte1    

    #____________________________________________________________________________________________________
    #_____________________VUES_____________________________________________________________________________

def carteAnomalieStatiqueRachis():
    
    #___________________ saisie de nombre: range_____________
        item1 = Item(titre_item="angle de Cobb", label_element=" Angle", categorie="", formule="Hyperlordose avec un angle de Cobb (en degré), estimé à ", defaut= "", optionnel="non", cible="", mini=0, maxi=100, tooltip="angle entre le plateau supérieur de la vertèbre limite supérieure et le plateau inférieur de la vertèbre limite inférieure")   
        listeRange= [item1]

    #_________________SELECT__________________

        #Select1
        item1 = Item(titre_item="complexe", label_element="déformation scoliotique complexe, centrée sur ", formule="déformation scoliotique complexe, centrée sur ", categorie="", defaut= "", optionnel="non", cible="",  )   
        item2 = Item(titre_item="à convexité droite", label_element="déformation scoliotique à convexité droite, centrée sur ", formule="déformation scoliotique à convexité droite, centrée sur ", categorie="",  defaut= "", optionnel="non", cible="", )   
        item3 = Item(titre_item="à convexité gauche", label_element="déformation scoliotique à convexité gauche, centrée sur ", formule="déformation scoliotique à convexité gauche, centrée sur ", categorie="",  defaut= "", optionnel="non", cible="", )   

        select1 = Select(titre="déformation scoliotique", listeOption=[item1,item2,item3])

        #liste
        listeSelect= [select1]
        for select in listeSelect:
            select.tooltip = select.titre




        carte1 = Carte(titre = "AnomalieStatiqueRachis", listeSelect = listeSelect, listeRange = listeRange)
        return carte1    

    #____________________________________________________________________________________________________
    #_____________________VUES_____________________________________________________________________________

def carteLocalisationRachis():
    
    """#___________________ saisie de nombre: range_____________
        item1 = Item(titre_item="angle de Cobb", label_element=" Angle", categorie="", formule="Hyperlordose avec un angle de Cobb (en degré), estimé à ", defaut= "", optionnel="non", cible="", mini=0, maxi=100, tooltip="angle entre le plateau supérieur de la vertèbre limite supérieure et le plateau inférieur de la vertèbre limite inférieure")   
       listeRange= [item1]"""

    #_________________SELECT__________________


    #rachis cervical:
    listeCervical= []
    for i in range (1,7):
        i = str(i)
        item = Item(titre_item="C"+i, label_element="C"+i, formule="localisation: C"+i, categorie="", defaut= "", optionnel="non", cible="",  )   
        listeCervical.append(item)
   
    #rachis dorsal:
    listeDorsal= []
    for i in range (1,12):
        i = str(i)
        item = Item(titre_item="T"+i, label_element="T"+i, formule="localisation: T"+i, categorie="", defaut= "", optionnel="non", cible="",  )   
        listeDorsal.append(item) 

    #rachis lombaire:
    listeLombaire= []
    for i in range (1,5):
        i = str(i)
        item = Item(titre_item="S"+i, label_element="S"+i, formule="localisation: S"+i, categorie="", defaut= "", optionnel="non", cible="",  )   
        listeDorsal.append(item)   


    select1 = Select(titre="Cervical", listeOption=listeCervical)
    select2 = Select(titre="Dorsal", listeOption=listeDorsal)
    select3 = Select(titre="Lombaire", listeOption=listeLombaire)

    #liste
    listeSelect= [select1, select2, select3]
    for select in listeSelect:
        select.tooltip = select.titre

    listeRange = []


    carte1 = Carte(titre = "carteLocalisationRachis", listeSelect = listeSelect, listeRange = listeRange)
    return carte1    

#____________________________________________________________________________________________________
#_____________________VUES_____________________________________________________________________________



#_______________________________________________


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
            self.rubriques =["scanner", "echographie", "radiographies", "irm", "gestion_patients"]
      
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

    return render(request, 'radio/radiographies.html', {"liste": Item.liste, "titre": titre})



#Irm
def irm(request):
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
      
   
    Item(region_anatomique= "cerebrale" ,sous_rubriques= ["cerebrale"],adresseImage="images/thorax.png" )        
    Item(region_anatomique= "coeur" ,sous_rubriques= ["cardiaque"],adresseImage="")
    Item(region_anatomique= "gynécologie" ,sous_rubriques= ["pelvienne"],adresseImage="" )
    Item(region_anatomique= "osteo-articulaire" ,sous_rubriques= ["bassin", "hanches", "cuisse", "genou", "jambe", "cheville"],adresseImage="" )
    Item(region_anatomique= "digestif" ,sous_rubriques= ["entéro", "foie", "pancréas", "biliaire"],adresseImage="" )
    Item(region_anatomique= "urinaire" ,sous_rubriques= ["rein", "véssie", "prostate"],adresseImage="" )


    titre="irm"

    return render(request, 'irm/irm.html', {"liste": Item.liste, "titre": titre})

def irm_cardiaque(request):

    carte1 = carteAnomalieCinetiqueCardiaque()
    listeCarte = [carte1]

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="ischémie", categorie="indication", formule="Bilan dans un contexte de cardiopathie ischémique", defaut= "", optionnel="non",)   
    Item(titre_item="INDICATION", label_element="DAVD", categorie="indication", formule="Recherche de signes de dysplasie arythmogène du ventricule droit", defaut= "", optionnel="non", cible="resultatDavd")
    Item(titre_item="INDICATION", label_element="CMH", categorie="indication", formule="Recherche d'argument pour une myocardiopathie hypertrophique (CMH)", defaut= "", optionnel="non")
    Item(titre_item="INDICATION", label_element="autre", categorie="indication", formule="", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de cheville gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "IRM cardiaque avec séquences de localisation et cine multiplanaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-DAVD
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies cinétiques", categorie="resultatDavd", formule="Anomalies cinétiques:", defaut= "Pas d'anomalie de la cinétique segmentaire ni globale des ventricules droit et gauche", optionnel="oui", dialog="anomalieCinetiqueCardiaque") 
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies morphologiques", categorie="resultatDavd", formule="Anomalies morphologiques:", defaut= "Pas d'anomalie morphologique cavitaire ni pariétale cardiaque.", optionnel="oui") 
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies quantitatives", categorie="resultatDavd", formule="Anomalies quantitatives:", defaut= "Pas d'anomalie notable des paramètres quantitatifs : FEVG: %, FEVD: %, VTDi: ml/m2, VTSi: ml/m2", optionnel="oui"  )
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies du réhaussement tardif", categorie="resultatDavd", formule="Anomalies du réhaussement tardif des parois myocardiques", defaut="Pas d'anomalie du réhaussement tardif des parois myocardiques", optionnel="oui") 
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="fracture ostéo-chondrale du talus", categorie="resultat_davd", formule="Fracture ostéo-chondrale du talus: ...", defaut= "intégrité du dôme du talus", optionnel="oui" )
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="arrachement osseux 5ème métatarsien", categorie="resultat_davd", formule="Arrachement osseux à l'insertion du 5ème métatarsien", defaut= "pas de signe d'arrachement osseux à l'insersion du tendon du court fibulaire sur la base du 5ème métatarsion", optionnel="oui" )
   


    #RESULTATS_Autres

    Item(titre_item="PAR AILLEURS:", label_element="pleurale", categorie="resultat_autre", formule="Anomalie pleurale:", 
    defaut= "Pas d'anomalie osseuse", optionnel="non")
    Item(titre_item="PAR AILLEURS:", label_element="péricardique", categorie="resultat_autre", formule="Anomalie péricardique:", 
    defaut= "Pas d'épanchement ni épaississement du péricarde", optionnel="non")
    Item(titre_item="PAR AILLEURS:", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    defaut= "pas d'anomalie notable des parties molles périphériques", optionnel="non")
    Item(titre_item="PAR AILLEURS:", label_element="pulmonaire", categorie="resultat_autre", defaut= "Pas d'anomalie notable du parenchyme pulmonaire dans le champ d'exploration.", optionnel="non", formule="Anomalie pulmonaire:")
    



    c = CRTYPE (  
                                indication="Bilan ", 
                                technique="IRM cardiaque, séquences ciné et de localisation multiplannaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", 
                                resultat="Analyse morphologique:xxPas d'anomalie morphologique cavitaire ni pariétale cardiaque.xxxxAnalyse cinétique:xxPas d'anomalie de la cinétique de contraction segmentaire ni globale des parois ventriculaires.xxPas d'agument pour une valvulopathie aortique ni mitrale.xxxxAnalyse du réhaussement:xxPas d'anomalie notable de la perfusion myocardique.xxPas d'anomalie du réhaussement tardif du myocardexxxxParamètres quantitatifs:xxFEVG: %, FEVD: %, VTDi: ml/m2, VTSi: ml/m2", 
                                conclusion="Pas d'anomalie notable retenue."

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "irm cardiaque" 
    page = "irm_cardiaque"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  
    

    return render(request, 'irm/irm_cardiaque.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType, "listeCarte":listeCarte})

def irm_cerebrale(request):

    #carte1 = carteAnomalieCinetiqueCardiaque()
    #listeCarte = [carte1]

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="céphalées", categorie="indication", formule="Bilan dans un contexte de cardiopathie ischémique", defaut= "", optionnel="non",)   
    Item(titre_item="INDICATION", label_element="suspicion d'AVC", categorie="indication", formule="Recherche de signes de dysplasie arythmogène du ventricule droit", defaut= "", optionnel="non", cible="resultatDavd")
    #Item(titre_item="INDICATION", label_element="CMH", categorie="indication", formule="Recherche d'argument pour une myocardiopathie hypertrophique (CMH)", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="autre", categorie="indication", formule="", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de cheville gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "IRM cardiaque avec séquences de localisation et cine multiplanaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-DAVD
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies cinétiques", categorie="resultatDavd", formule="Anomalies cinétiques:", defaut= "Pas d'anomalie de la cinétique segmentaire ni globale des ventricules droit et gauche", optionnel="oui", dialog="anomalieCinetiqueCardiaque") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies morphologiques", categorie="resultatDavd", formule="Anomalies morphologiques:", defaut= "Pas d'anomalie morphologique cavitaire ni pariétale cardiaque.", optionnel="oui") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies quantitatives", categorie="resultatDavd", formule="Anomalies quantitatives:", defaut= "Pas d'anomalie notable des paramètres quantitatifs : FEVG: %, FEVD: %, VTDi: ml/m2, VTSi: ml/m2", optionnel="oui"  )
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies du réhaussement tardif", categorie="resultatDavd", formule="Anomalies du réhaussement tardif des parois myocardiques", defaut="Pas d'anomalie du réhaussement tardif des parois myocardiques", optionnel="oui") 
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="fracture ostéo-chondrale du talus", categorie="resultat_davd", formule="Fracture ostéo-chondrale du talus: ...", defaut= "intégrité du dôme du talus", optionnel="oui" )
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="arrachement osseux 5ème métatarsien", categorie="resultat_davd", formule="Arrachement osseux à l'insertion du 5ème métatarsien", defaut= "pas de signe d'arrachement osseux à l'insersion du tendon du court fibulaire sur la base du 5ème métatarsion", optionnel="oui" )
   


    #RESULTATS_Autres

    #Item(titre_item="PAR AILLEURS:", label_element="pleurale", categorie="resultat_autre", formule="Anomalie pleurale:", 
    #defaut= "Pas d'anomalie osseuse", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="péricardique", categorie="resultat_autre", formule="Anomalie péricardique:", 
    #defaut= "Pas d'épanchement ni épaississement du péricarde", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    #defaut= "pas d'anomalie notable des parties molles périphériques", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="pulmonaire", categorie="resultat_autre", defaut= "Pas d'anomalie notable du parenchyme pulmonaire dans le champ d'exploration.", optionnel="non", formule="Anomalie pulmonaire:")
    



    c = CRTYPE (  
                                indication="Bilan ", 
                                technique="IRM cérébrale avec séquences sagittal T1, axial T2 FLAIR, diffusion axiale, 3DT1 après gadolinium", 
                                resultat="Pas de lésion focale ni infiltrante parenchymateuse cérébrale.xxPasde décollement des espaces de la convexité.xxPas de signes d'HTICxxPas d'anomalie cisterno-ventriculaire.xxPas de prise de contraste pathologique cérébro-méningée.xxPas d'anomalie artérielle ni veineuse patente.xxxxPas d'anomalie notable osseuse, des parties molles périphériques.", 
                                conclusion="Pas d'anomalie notable retenue."

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "irm_cerebrale" 
    page = "irm_cerebrale"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  
    

    return render(request, 'irm/irm_cerebrale.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def irm_foie(request):

    #carte1 = carteAnomalieCinetiqueCardiaque()
    #listeCarte = [carte1]

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="dépistage de CHC", categorie="indication", formule="Bilan dans un contexte de cardiopathie ischémique", defaut= "", optionnel="non",)   
    Item(titre_item="INDICATION", label_element="caractérisation lésionnelle", categorie="indication", formule="Recherche de signes de dysplasie arythmogène du ventricule droit", defaut= "", optionnel="non", cible="resultatDavd")
    #Item(titre_item="INDICATION", label_element="CMH", categorie="indication", formule="Recherche d'argument pour une myocardiopathie hypertrophique (CMH)", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="autre", categorie="indication", formule="", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de cheville gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "IRM cardiaque avec séquences de localisation et cine multiplanaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-DAVD
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies cinétiques", categorie="resultatDavd", formule="Anomalies cinétiques:", defaut= "Pas d'anomalie de la cinétique segmentaire ni globale des ventricules droit et gauche", optionnel="oui", dialog="anomalieCinetiqueCardiaque") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies morphologiques", categorie="resultatDavd", formule="Anomalies morphologiques:", defaut= "Pas d'anomalie morphologique cavitaire ni pariétale cardiaque.", optionnel="oui") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies quantitatives", categorie="resultatDavd", formule="Anomalies quantitatives:", defaut= "Pas d'anomalie notable des paramètres quantitatifs : FEVG: %, FEVD: %, VTDi: ml/m2, VTSi: ml/m2", optionnel="oui"  )
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies du réhaussement tardif", categorie="resultatDavd", formule="Anomalies du réhaussement tardif des parois myocardiques", defaut="Pas d'anomalie du réhaussement tardif des parois myocardiques", optionnel="oui") 
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="fracture ostéo-chondrale du talus", categorie="resultat_davd", formule="Fracture ostéo-chondrale du talus: ...", defaut= "intégrité du dôme du talus", optionnel="oui" )
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="arrachement osseux 5ème métatarsien", categorie="resultat_davd", formule="Arrachement osseux à l'insertion du 5ème métatarsien", defaut= "pas de signe d'arrachement osseux à l'insersion du tendon du court fibulaire sur la base du 5ème métatarsion", optionnel="oui" )
   


    #RESULTATS_Autres

    #Item(titre_item="PAR AILLEURS:", label_element="pleurale", categorie="resultat_autre", formule="Anomalie pleurale:", 
    #defaut= "Pas d'anomalie osseuse", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="péricardique", categorie="resultat_autre", formule="Anomalie péricardique:", 
    #defaut= "Pas d'épanchement ni épaississement du péricarde", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    #defaut= "pas d'anomalie notable des parties molles périphériques", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="pulmonaire", categorie="resultat_autre", defaut= "Pas d'anomalie notable du parenchyme pulmonaire dans le champ d'exploration.", optionnel="non", formule="Anomalie pulmonaire:")
    



    c = CRTYPE (  
                                indication="Bilan ", 
                                technique="IRM hépatique avec séquences coronale T2 HASTE, axial T2, T1 in et out Phase, diffusion axiale, T1 axial après gadolinium, multiphasique", 
                                resultat="Foie non dysmorphique, non stéatosique.xxPas de lésion focalisée hépatique mise en évidence.xxPerméabilité du système porte et veineux sus hépatique.xxPas de dilatation des voies biliaires intra ni extra-hépatique.xxxxPas d'anomalie notable viscérale, ganglionnaire, péritonéale, vasculaire, osseuse, des parties molles périphériques décelée par ailleurs.", 
                                conclusion="Pas d'anomalie notable retenue."

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "irm_foie" 
    page = "irm_foie"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  
    

    return render(request, 'irm/irm_foie.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def irm_genou(request):

    #carte1 = carteAnomalieCinetiqueCardiaque()
    #listeCarte = [carte1]

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="bilan post traumatique", categorie="indication", formule="Bilan...", defaut= "", optionnel="non",)   
    Item(titre_item="INDICATION", label_element="gonalgies non traumatiques", categorie="indication", formule="Bilan ...", defaut= "", optionnel="non", cible="")
    #Item(titre_item="INDICATION", label_element="CMH", categorie="indication", formule="Recherche d'argument pour une myocardiopathie hypertrophique (CMH)", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="autre", categorie="indication", formule="", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de cheville gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "IRM cardiaque avec séquences de localisation et cine multiplanaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-DAVD
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies cinétiques", categorie="resultatDavd", formule="Anomalies cinétiques:", defaut= "Pas d'anomalie de la cinétique segmentaire ni globale des ventricules droit et gauche", optionnel="oui", dialog="anomalieCinetiqueCardiaque") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies morphologiques", categorie="resultatDavd", formule="Anomalies morphologiques:", defaut= "Pas d'anomalie morphologique cavitaire ni pariétale cardiaque.", optionnel="oui") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies quantitatives", categorie="resultatDavd", formule="Anomalies quantitatives:", defaut= "Pas d'anomalie notable des paramètres quantitatifs : FEVG: %, FEVD: %, VTDi: ml/m2, VTSi: ml/m2", optionnel="oui"  )
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies du réhaussement tardif", categorie="resultatDavd", formule="Anomalies du réhaussement tardif des parois myocardiques", defaut="Pas d'anomalie du réhaussement tardif des parois myocardiques", optionnel="oui") 
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="fracture ostéo-chondrale du talus", categorie="resultat_davd", formule="Fracture ostéo-chondrale du talus: ...", defaut= "intégrité du dôme du talus", optionnel="oui" )
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="arrachement osseux 5ème métatarsien", categorie="resultat_davd", formule="Arrachement osseux à l'insertion du 5ème métatarsien", defaut= "pas de signe d'arrachement osseux à l'insersion du tendon du court fibulaire sur la base du 5ème métatarsion", optionnel="oui" )
   


    #RESULTATS_Autres

    #Item(titre_item="PAR AILLEURS:", label_element="pleurale", categorie="resultat_autre", formule="Anomalie pleurale:", 
    #defaut= "Pas d'anomalie osseuse", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="péricardique", categorie="resultat_autre", formule="Anomalie péricardique:", 
    #defaut= "Pas d'épanchement ni épaississement du péricarde", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    #defaut= "pas d'anomalie notable des parties molles périphériques", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="pulmonaire", categorie="resultat_autre", defaut= "Pas d'anomalie notable du parenchyme pulmonaire dans le champ d'exploration.", optionnel="non", formule="Anomalie pulmonaire:")
    



    c = CRTYPE (  
                                indication="Bilan ", 
                                technique="IRM du genou 3 plans DP FAT-SAT, sagittal T1", 
                                resultat="Pas d'anomalie des ligaments croisés antérieur et postérieur, des ligaments collatéraux latéral et médial.xxIntégrité de l'appareil extenseur et des ailerons rotuliens.xxPas de signes de chondropathie significative des compartiments fémoro-patellaire et fémoro-tibiaux.xxIntégrité des ménisques.xxPas de lésion osseuse d'allure traumatique, inflammatoire, malformative, néoplasique.xxPas d'épanchement intra-articulaire significatif.xxPas de kyste poplité.xxPas d'anomalie notable musculo-tendineuse, vasculo-nerveuse abarticulaire.", 
                                conclusion="Pas d'anomalie notable retenue."

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "irm du genou" 
    page = "irm_genou"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  
    

    return render(request, 'irm/irm_genou.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def irm_rachis_lombaire(request):

    #carte1 = carteAnomalieCinetiqueCardiaque()
    #listeCarte = [carte1]

    remise_a_zero_des_items()
      
     #INDICATIONS:
    Item(titre_item="INDICATION", label_element="lombo-sciatalgie", categorie="indication", formule="Bilan...", defaut= "", optionnel="non",)   
    Item(titre_item="INDICATION", label_element="Bilan post traumatiques", categorie="indication", formule="Bilan ...", defaut= "", optionnel="non", cible="")
    #Item(titre_item="INDICATION", label_element="CMH", categorie="indication", formule="Recherche d'argument pour une myocardiopathie hypertrophique (CMH)", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="autre", categorie="indication", formule="", defaut= "", optionnel="non")
    #Item(titre_item="INDICATION", label_element="gauche", categorie="indication", formule="de cheville gauche", defaut= "", optionnel="non")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "IRM cardiaque avec séquences de localisation et cine multiplanaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT-DAVD
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies cinétiques", categorie="resultatDavd", formule="Anomalies cinétiques:", defaut= "Pas d'anomalie de la cinétique segmentaire ni globale des ventricules droit et gauche", optionnel="oui", dialog="anomalieCinetiqueCardiaque") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies morphologiques", categorie="resultatDavd", formule="Anomalies morphologiques:", defaut= "Pas d'anomalie morphologique cavitaire ni pariétale cardiaque.", optionnel="oui") 
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies quantitatives", categorie="resultatDavd", formule="Anomalies quantitatives:", defaut= "Pas d'anomalie notable des paramètres quantitatifs : FEVG: %, FEVD: %, VTDi: ml/m2, VTSi: ml/m2", optionnel="oui"  )
    #Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES DE DAVD", label_element="anomalies du réhaussement tardif", categorie="resultatDavd", formule="Anomalies du réhaussement tardif des parois myocardiques", defaut="Pas d'anomalie du réhaussement tardif des parois myocardiques", optionnel="oui") 
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="fracture ostéo-chondrale du talus", categorie="resultat_davd", formule="Fracture ostéo-chondrale du talus: ...", defaut= "intégrité du dôme du talus", optionnel="oui" )
    #Item(titre_item="ELEMENTS SPECIFIQUES DE DAVD", label_element="arrachement osseux 5ème métatarsien", categorie="resultat_davd", formule="Arrachement osseux à l'insertion du 5ème métatarsien", defaut= "pas de signe d'arrachement osseux à l'insersion du tendon du court fibulaire sur la base du 5ème métatarsion", optionnel="oui" )
   


    #RESULTATS_Autres

    #Item(titre_item="PAR AILLEURS:", label_element="pleurale", categorie="resultat_autre", formule="Anomalie pleurale:", 
    #defaut= "Pas d'anomalie osseuse", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="péricardique", categorie="resultat_autre", formule="Anomalie péricardique:", 
    #defaut= "Pas d'épanchement ni épaississement du péricarde", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    #defaut= "pas d'anomalie notable des parties molles périphériques", optionnel="non")
    #Item(titre_item="PAR AILLEURS:", label_element="pulmonaire", categorie="resultat_autre", defaut= "Pas d'anomalie notable du parenchyme pulmonaire dans le champ d'exploration.", optionnel="non", formule="Anomalie pulmonaire:")
    



    c = CRTYPE (  
                                indication="Bilan ", 
                                technique="IRM du rachis lombaire, sagittal T1, Coronal T2 STIR, 3D T2", 
                                resultat="Pas d'anomalie notable de la statique rachidienne lombaire.xxPas d'étroitesse constitutionnelle ni acquise du canal osseux rachidien lombaire.xxPas de lésion osseuse d'allure traumatique, inflammatoire, néoplasique.xxPas de remaniements discarthrosiques patents.xxPas de discopathie significative.xxPas d'anomalie du cône médullaire ni des racines de la queue de cheval.xxPas d'anomalie patente des parties molles péri-rachidiennes", 
                                conclusion="Pas d'anomalie notable retenue."

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "irm_rachis_lombaire" 
    page = "irm_rachis_lombaire"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  
    

    return render(request, 'irm/irm_rachis_lombaire.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def irm_prostate(request):

    carte1 = carteIndicationProstate()
    carte2 = carteCalculVolume()
    carte3 = carteProstateLesion()
    listeCarte = [carte1, carte2]

    remise_a_zero_des_items()
      
     #INDICATIONS:

    Item(titre_item="INDICATION", label_element="Suspicion de néoplasie", categorie="indication", formule="Suspicion de néoplasie prostatique \n", defaut= "", optionnel="non",cible="resultatNeoplasie", dialog="indicationProstate")   
    Item(titre_item="INDICATION", label_element="Extension loco-régionale", categorie="indication", formule="Bilan d'extension locorégionale dans un contexte de néoplasie prostatique", defaut= "", optionnel="non", cible="resultatNeoplasie", dialog="indicationProstate")
    Item(titre_item="INDICATION", label_element="Autre:", categorie="indication", formule="Bilan d'extension locorégionale dans un contexte de néoplasie prostatique", defaut= "", optionnel="non", cible="resultatNeoplasie", dialog="indicationProstate")


    #TECHNIQUE: 
    #probleme
    Item(titre_item="TECHNIQUE", label_element="mauvaise qualité", categorie="technique", formule="Examen de qualité sous-optimale", defaut= "IRM cardiaque avec séquences de localisation et cine multiplanaires, séquences après injection de gadolinium pour étude de la perfusion myocardique et du réhaussement tardif.", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise incidence", categorie="technique", formule=": indicence ... non stricte", defaut= "", optionnel="non") 
    #Item(titre_item="TECHNIQUE", label_element="mauvaise exposition", categorie="technique", formule=": exposition inadaptée du cliché", defaut= "", optionnel="non") 
    

    #RESULTAT
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES NEOLASIE", label_element="Volume de la glande", categorie="resultatNeoplasie", formule="Volume de la glande(cc) = ", defaut= "Volume prostatique normal", optionnel="oui", dialog="volumeProstate") 
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES NEOLASIE", label_element="Lésion focale", categorie="resultatNeoplasie", formule="Lésion focale", defaut= "Pas de lésion focalisée prostatique suspecte", optionnel="oui", dialog="prostateLesion") 
    Item(titre_item="RESULTAT: ELEMENTS SPECIFIQUES NEOLASIE", label_element="Hypertrophie bénigne", categorie="resultatNeoplasie", formule="Hypertrophie bénigne prostatique avec un signal hétérogène de la zone transitionnelle", defaut= "", optionnel="oui", dialog="") 

        


    #RESULTATS_Autres

    Item(titre_item="PAR AILLEURS:", label_element="os", categorie="resultat_autre", formule="Anomalie osseuse:", 
    defaut= "Pas d'anomalie osseuse", optionnel="non")
    Item(titre_item="PAR AILLEURS:", label_element="anomalie parties molles périphériques", categorie="resultat_autre", formule="Anomalie des parties molles périphériques: ", 
    defaut= "pas d'anomalie notable des parties molles périphériques", optionnel="non")
    



    c = CRTYPE (  
                                indication="Suspcicion de néoplasie prostatique. PSA=  ng/ml.", 
                                technique="IRM prostatique multiparamétrique avec séquences en T2 (2 plans), en diffusion, dynamiques T1EG après gadolinium." ,
                                resultat="Volume de la glande: Xg. xx Pas de lésion focalisée prostatique suspecte identifiée.xxPas d'anomalie de signal focale de la glande.xxPas de prise de contraste suspecte.xxPas de lésion en restriction de diffusion.xxPas d'adénopathie loco-régionale.xxxxPas d'anomalie viscérale, osseuse, des parties molles périphériques décelée par ailleurs dans le champ d'exploration.",
                                conclusion="Pas d'anomalie notable retenue.",

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "irm prostatique" 
    page = "irm_prostate"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres 
    carteSpecifique = carte3 
    

    return render(request, 'irm/irm_prostate.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType, "listeCarte":listeCarte, "carteSpecifique":carteSpecifique})




#scanner
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





#radiographies
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
    url = "radiographies/pulmonaire" 
    

    return render(request, 'radio/radiographies_pulmonaire.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_cheville(request):

    carte1 = carteFracture()
    listeCarte = [carte1]

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
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture malléolaire", categorie="resultat_traumatisme", formule="Fracture de la malléole ...", defaut= "Intégrité des malléoles", optionnel="oui", dialog="fracture") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture fibulaire", categorie="resultat_traumatisme", formule="Fracture fibulaire", defaut= "intégrité de la fibula", optionnel="oui" ,dialog="fracture") 
    Item(titre_item="ELEMENTS SPECIFIQUES DE TRAUMATISME", label_element="fracture tibiale", categorie="resultat_traumatisme", formule="Fracture tibiale", defaut= "intégrité du tibia", optionnel="oui" ,dialog="fracture" )
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
    

    return render(request, 'radio/radiographies_cheville.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType, "listeCarte":listeCarte})

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















    return render(request, 'radio/radiographies_cheville.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_coude.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_poignet.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_epaule.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_rachis_lombaire(request):

    carte1 = carteAnomalieStatiqueRachis()
    carte2 = carteLocalisationRachis()
    listeCarte = [carte1, carte2]

    remise_a_zero_des_items()

    #INDICATIONS:
    Item(titre_item="INDICATION", label_element="lombalgies chroniques", categorie="indication", formule="Bilan de lombalgies chroniques", defaut= "", optionnel="non", cible="resultat_lombalgies_chroniques")   
    Item(titre_item="INDICATION", label_element="lombalgies subaigues", categorie="indication", formule="Bilan de lombalgies subaigues", defaut= "", optionnel="non") 
    Item(titre_item="INDICATION", label_element="traumatisme", categorie="indication", formule="bilan post-traumatique", defaut= "", optionnel="non", cible="typeTraumatisme")      
    

    #TECHNIQUE:
    #base
    Item(titre_item="TECHNIQUE", label_element="avec profile", categorie="technique", formule="Radiographie thoracique de face et de profile", defaut= "Radiographie thoracique de face", optionnel="non") 
    #probleme


    #RESULTATS 
    Item(titre_item="RESULTATS", label_element="anomalie de la statique", categorie="resultat", formule="-Anomalies de la statiques rachidienne lombaire : ", defaut= "-Pas d'anomalie de la statique rachidienne lombaire", optionnel="non", dialog="AnomalieStatiqueRachis") 
    Item(titre_item="RESULTATS", label_element="remaniements dégénératifs", categorie="resultat", formule="-Remaniements dégénératifs discarthrosiques centrés sur  ", defaut= "-Pas de remaniement disco-dégénératif significatif", optionnel="non") 
    Item(titre_item="RESULTATS", label_element="spondylolisthesis", categorie="resultat", formule="-Spondylolisthesis: ", defaut= "", optionnel="non") 
    Item(titre_item="RESULTATS", label_element="lésion focalisée", categorie="resultat", formule="-Lésion osseuse indéterminée ", defaut= "-Pas de lésion osseuse suspecte de néoplasie", optionnel="non") 
    Item(titre_item="RESULTATS", label_element="fracture", categorie="resultat", formule=" Fracture", defaut= "-Pas de lésion d'allure traumatique", optionnel="non", dialog="carteLocalisationRachis") 
    Item(titre_item="RESULTATS", label_element="signes de spondylarthropathie", categorie="resultat", formule="-Signes pouvant orienter vers une spondylarthropathie", defaut= "-Pas de signe d'atteinte inflammatoire", optionnel="non", cible="spondylarthropathie") 
    Item(titre_item="RESULTATS", label_element="déminéralisation", categorie="resultat", formule="-Déminéralisation diffuse de la trame osseuse", 
    defaut= "-Pas d'anomalie notable de la trame osseuse", optionnel="non")
    Item(titre_item="RESULTATS", label_element="anomalie des parties molles", categorie="resultat", formule="-Anomalie des parties molles:", 
    defaut= "-Pas d'anomalie des parties molles", optionnel="non")

    #SPONDYLARTHROPATHIE
    Item(titre_item="--> signes de spondylarthropathie:", label_element="spondylite de Romanus", categorie="spondylarthropathie", formule=" -érosion du coin supérieur de la vertèbre", defaut= "", optionnel="oui") 
    Item(titre_item="--> signes de spondylarthropathie:", label_element="syndesmophytes", categorie="spondylarthropathie", formule=" -ponts osseux à base étroite et direction verticale", defaut= "", optionnel="oui") 
    Item(titre_item="--> signes de spondylarthropathie:", label_element="mise au carré", categorie="spondylarthropathie", formule=" -mise au carré des vertèbres", defaut= "", optionnel="oui") 
    Item(titre_item="--> signes de spondylarthropathie:", label_element="arthrite interapophysaire", categorie="spondylarthropathie", formule=" -arthrite interapophysaire postérieure", defaut= "", optionnel="oui") 

              

    c = CRTYPE (  
                                indication="Bilan ", 
                                technique="radiographie du rachis lombaire, face et profil", 
                                resultat="Pas d'anomalie de la statique rachidienne lombaire.xxPas d'anomalie globale de la trame osseuse.xxPas de lésion focalisée d'allure traumatique, inflammatoire, suspecte de néoplasie.", 
                                conclusion="Pas d'anomalie significative retenue"

                                )

    #GUIDE INTERACTIF:

    E1 = Etape(question="la qualité de l'examen est-elle correcte?", titre="qualite", non="qualité d'examen insuffisante:",ouiCible="DescriptionAnomalieQualite", nonCible="statique", premiere="premiere")
    E2 = Etape(question="Existe-t-il des anomalies de la statique du rachis?", titre="statique", oui="anomalie de la statique rachidienne:", ouiCible="descriptionAnomalieStatique",  non="pas d'anomalie de la statique rachidienne", nonCible="")
    E3 = Etape(question="Décrivez l'anomalie", titre="descriptionAnomalieStatique", oui="", non="", widget="zoneDeTexte", ouiCible="localisationAnomalieStatique", nonCible="localisationAnomalieStatique")
    E4 = Etape(question="Decrivez sa localisation", titre="localisationAnomalieStatique", oui="", ouiCible="", nonCible="", non="", widget="zoneDeTexte")


    etapes = [E1, E2, E3, E4]
    guide = Guide(etapes=etapes)


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du rachis lombaire" 
    page = "radiographie_rachis_lombaire"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres 
 


    return render(request, 'radio/radiographies_rachis_lombaire.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "listeCarte":listeCarte, "compteRenduType":compteRenduType, "guide":guide,})

def radiographie_rachis_dorsal(request):


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





    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du rachis dorsal, face et profil", 
                                resultat="Pas d'anomalie de la statique rachidienne dorsale.xxPas d'anomalie globale de la trame osseuse.xxPas de lésion focalisée d'allure traumatique, inflammatoire, suspecte de néoplasie.", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du rachis dorsal" 
    page = "radiographie_rachis_dorsal"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radio/radiographies_rachis_dorsal.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

def radiographie_rachis_cervical(request):

      
    

    #INDICATIONS:
    Item(titre_item="INDICATION", label_element="cervicalgies chroniques", categorie="indication", formule="Bilan de dyspnée", defaut= "", optionnel="non")   
    Item(titre_item="INDICATION", label_element="bilan post traumatique", categorie="indication", formule="Douleurs thoraciques", defaut= "", optionnel="non") 
    

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


    


    c = CRTYPE (  
                                indication="Bilan post traumatique", 
                                technique="radiographie du rachis cervical, face et profil, cliché bouche ouverte", 
                                resultat="Pas d'anomalie de la statique rachidienne cervicale.xxPas d'anomalie globale de la trame osseuse.xxPas de lésion focalisée d'allure traumatique, inflammatoire, suspecte de néoplasie.", 
                                conclusion=""

                                )


    compteRenduType = CRTYPE.compte_rendu(c)

    titre = "radiographie du rachis cervical" 
    page = "radiographie_rachis_cervical"     
    liste_des_items= Item.liste_des_items
    liste_des_titres=Item.liste_des_titres  


    return render(request, 'radio/radiographies_rachis_cervical.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_main.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_pied.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_bassin.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_bras.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_avant-bras.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_cuisse.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})

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


    return render(request, 'radio/radiographies_jambe.html', {"titre": titre, "page": page, "liste_des_items":liste_des_items, "liste_des_titres":liste_des_titres, "compteRenduType":compteRenduType})





