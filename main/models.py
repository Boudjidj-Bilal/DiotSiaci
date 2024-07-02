from django.db import models
from django.utils import timezone 
# Create your models here.

class Articles(models.Model):
    title = models.CharField(max_length=128, default="") # On crée un champ title de type string avec 128 caractères maximum
    content = models.TextField(blank=True, default="") # On crée un champ content de type text
    publication_date = models.DateTimeField(default=timezone.now, blank=True) # On crée un champ publication_date de type DateTime qui prend la date et l'heure de la publication de l'article

    def __str__(self) -> str:
        return f"{self.title}" # Dans l'interface administration, on affiche les titles.

