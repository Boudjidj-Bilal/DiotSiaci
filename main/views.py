from django.shortcuts import render
from main.models import Articles
from django.shortcuts import redirect
from django.utils.translation import activate
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .utils import process_query, vectorDocuments, addDocumentDB, chatbotLLM, translation
import os


# Create your views here.

# Si l'appllication est lancé pour la première, au démarage on télécharge le model de texte génération sinon on l'importe simplement.

collection_name = 'mycollection'

def chatbotGpt2(request): # Fonction du chatbot pour le model gpt2.
    if request.method == 'POST': # On vérifie si la requête est de type Post.       
        user_message = request.POST.get("message")
        langueUser = request.LANGUAGE_CODE
        # langue = request
        if user_message: # Si on récupère bien le texte de l'utilisateur.
            # On le traduit en anglais pour qu'il soient compréhensible par le model gpt2:
            texteSortie = chatbotLLM(user_message, langueUser)
            return JsonResponse({'response': texteSortie}) # On retourne le texte en format json à la requête ajax du fichier script.js
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)
    else:
        return render(request, 'chatbot.html') 


def mainViews(request): # Page principal.
    articles = Articles.objects.filter()
    return render(request, 'main.html', context={"article_liste":articles}) #crée la page de la liste des articles.

def article(request, articleId): # Page détail d'un article.
    article = Articles.objects.get(id=articleId)
    return render(request, 'article.html', context={"article":article}) # Crée la page de la liste des articles.

def change_language(request, language_code): # On change la langue de l'application.
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    if language_code in dict(settings.LANGUAGES):
        activate(language_code)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)
    return response



@csrf_exempt
def chatbotRag(request):
    """
    Gère les interactions avec le chatbot.

    Args:
        request (HttpRequest): La requête HTTP reçue, avec une requête utilisateur dans le corps.

    Returns:
        JsonResponse: La réponse du chatbot sous forme JSON.
    """
    if request.method == 'POST':
        try:
            # Récupère et analyse les données JSON envoyées par l'utilisateur
            data = json.loads(request.body)
            user_query = data.get('query')

            # On récupère la langue de l'utilisateur 
            langueUser = request.LANGUAGE_CODE

            # Tradution du texte en Anglais :
            user_query = translation(user_query,Langue="en")
            
            # Traite la requête utilisateur et génère une réponse
            response = process_query(user_query, collection_name)
            
            # Tradution du texte dans la langue de l'utilisateur si besoin :
            if not langueUser == "en":
                response = translation(response,Langue=langueUser)

            return JsonResponse({'response': response})
        
        except json.JSONDecodeError:
            # Gère le cas où le JSON est invalide
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    # Affiche la page du chatbot si la méthode n'est pas POST
    return render(request, 'chatbotrag.html')



@csrf_exempt
def upload_files(request):
    """
    Gère l'upload de fichiers PDF et TXT pour traitement.

    Args:
        request (HttpRequest): La requête HTTP reçue, avec les fichiers à uploader.

    Returns:
        JsonResponse: Message de confirmation ou d'erreur.
    """
    if request.method == 'POST' and request.FILES.getlist('documents'):
        files = request.FILES.getlist('documents')
        allowed_extensions = ['.pdf', '.txt']
        file_paths = []

        # Vérifie que chaque fichier a une extension valide
        for file in files:
            if not any(file.name.endswith(ext) for ext in allowed_extensions):
                return JsonResponse({'error': 'Format de fichier invalide.Seuls les fichiers PDF et TXT sont permis.'}, status=400)

            # Enregistre chaque fichier dans le dossier 'uploads'
            path = os.path.join('uploads', file.name)
            with open(path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            file_paths.append(path)

        # Traite les fichiers uploadés
        chunks = vectorDocuments(file_paths)
        addDocumentDB(chunks, collection_name)
        
        # Renvoie une réponse de succès
        return JsonResponse({'message': 'Traitement réussi des fichiers.'}, status=200)
    
    # Affiche la page d'upload si la méthode n'est pas POST
    return render(request, 'upload.html')
