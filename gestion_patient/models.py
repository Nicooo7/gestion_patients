from django.db import models

# Create your models here.


class Demande(models.Model):
   
    degre_urgence_choix = (
        ('H24', 'H24'),
        ('H48', 'H48'),
        ('J7', 'J7'),
        ('programmer', 'programmer'),
    )
    
    type_examen = (
        ('scanner', 'scanner'),
        ('IRM', 'IRM'),
        ('echographie', 'echographie'),
        ('autre', 'autre'),
    )
    
    
    prenom = models.CharField(max_length=30)
    nom = models.CharField(max_length=30)
    ipp = models.PositiveIntegerField()
    degre_urgence = models.CharField(
        max_length=10,
        choices=degre_urgence_choix)
    type_examen= models.CharField(
        max_length=10,
        choices=type_examen)