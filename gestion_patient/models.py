#coding: utf-8
from django.db import models

# Create your models here.


class Demande(models.Model):
   
    degre_urgence_choix = (
        ('H24', 'H24'),
        ('immédiat', 'immédiat'),
    )
    
    type_examen_choix = (
        ('scanner cerebral', 'scanner cerebral'),
        ('scanner AP', 'scanner AP'),
        ('scanner TAP', 'scanner TAP'),
        ('angioscanner pulmonaire', 'angioscanner pulmonaire'),
        ('uroscanner', 'uroscanner'),
        ('scanner Thoracique', 'scanner thoracique'),
    )
    injection_choix = (
        ('oui', 'oui'),
        ('non', 'non'),
        ('à voir', 'à voir')
    )
    realisation_choix =(
        ('oui', 'oui'),
        ('non', 'non'),
    )
    
    
    prenom = models.CharField(max_length=30)
    nom = models.CharField(max_length=30)
    indication = models.CharField(max_length=300, null=True)
    degre_urgence = models.CharField(
        max_length=10,
        choices=degre_urgence_choix)
    type_examen= models.CharField(
        max_length=30,
        choices=type_examen_choix)
    injection = models.CharField(
        max_length=30,
        choices=injection_choix)
    realisation = models.CharField(
        max_length=30, 
        choices=realisation_choix, null=True, default="non")
    suppression = models.CharField(
        max_length=10,
        choices=realisation_choix,null=True, default="non")
    heure= models.DateTimeField(null = True)
    
