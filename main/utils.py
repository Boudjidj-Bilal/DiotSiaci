
import os
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from deep_translator import GoogleTranslator
from transformers import pipeline



# generation_texte = pipeline("text-generation", top_k=4, num_return_sequences=1) # Par défaut on utilise GPT2

# Configuration des modèles et du client Chroma
model_embedding = "sentence-transformers/all-MiniLM-L6-v2"
#model_embedding = "sentence-transformers/all-mpnet-base-v2"

localhost = 'localhost'
port = '8001'

# Initialisation du modèle d'embedding et du client Chroma
embedding_model = SentenceTransformer(model_embedding)
embedding_function = SentenceTransformerEmbeddings(model_name=model_embedding)
chroma_client = chromadb.HttpClient(host=localhost, port=port, settings=Settings())
model_name = "openai-community/gpt2"
#model_name = "microsoft/phi-2"

# Chargement du modèle de langage de generation texte et du tokenizer
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# tokenizer = AutoTokenizer.from_pretrained("model_name")
# model = AutoModelForCausalLM.from_pretrained("model_name")


# model.save_pretrained("./my_model_directory/")  # only needed first run
# model = StableDiffusionPipeline.from_pretrained("./my_model_directory/")
# chatbot_app/utils.py



def vectorDocuments(files, chunk_size=1000, chunk_overlap=100):
    """
    Divise les documents en petits chunks pour le traitement.

    Args:
        files (list): Liste des chemins des fichiers à traiter.
        chunk_size (int): Taille maximale de chaque chunk de texte.
        chunk_overlap (int): Nombre de caractères qui se chevauchent entre les chunks.

    Returns:
        list: Liste des chunks de texte extraits des documents.
    """
    chunked_documents = []
    for file in files:
        # Utilise le chargeur approprié selon l'extension du fichier
        loader = PyPDFLoader(file) if file.endswith('.pdf') else TextLoader(file)
        document = loader.load()
        # Divise le document en chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_documents(document)
        chunked_documents.extend(chunks)
    return chunked_documents

def addDocumentDB(chunks, collection_name):
    """
    Ajoute des chunks de documents à la base de données Chroma.

    Args:
        chunks (list): Liste des chunks de documents à ajouter.
        collection_name (str): Nom de la collection dans ChromaDB.
    """
    # Vérifie si la collection existe, la supprime si c'est le cas
    if collection_name in [col.name for col in chroma_client.list_collections()]:
        chroma_client.delete_collection(name=collection_name)
    # Ajoute les documents à ChromaDB
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        collection_name=collection_name,
        client=chroma_client,
    )
    print(f"Ajouté {len(chunks)} chunks à la base de données Chroma")

def searchSimilarity(query, collection_name):
    """
    Recherche des documents similaires dans la base de données Chroma.

    Args:
        query (str): Chaîne de requête à rechercher.
        collection_name (str): Nom de la collection dans ChromaDB.

    Returns:
        str: Le document le plus similaire trouvé.
    """
    collection = chroma_client.get_collection(name=collection_name)
    query_vector = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=2,
        include=['distances', 'embeddings', 'documents', 'metadatas'],
    )
    return results['documents'][0][0]

def gradGeneration(similarity_result, query, max_new_tokens=50, do_sample=True, num_return_sequences=1, early_stopping=True):
    """
    Génère une réponse basée sur le résultat de similarité et la requête.

    Args:
        similarity_result (str): Texte du document le plus similaire.
        query (str): Requête originale de l'utilisateur.

    Returns:
        str: Réponse générée.
    """
    # Construit l'entrée pour le modèle de langage
    context_q_r = f"CONTEXT:\n{similarity_result}\n\nQUESTION:\n{query}\n\nANSWER: "
    input_text = get_system_message_rag(context_q_r)

    # Tokenisation et génération de la réponse
    inputs = tokenizer.encode(input_text, return_tensors='pt')
    outputs = model.generate(
        inputs,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        num_return_sequences=num_return_sequences,
        early_stopping=early_stopping
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(input_text):].strip()

def get_system_message_rag(content):
    """
    Formate le message système pour le modèle de génération de réponses.

    Args:
        content (str): Contenu du contexte et de la question.

    Returns:
        str: Message système formaté.
    """

    return f"""
INSTRUCTIONS:
You are a QA assistant and you are an expert consultant helping executive advisors to get relevant information from internal documents.

Generate your response by following the steps below:
1. Select the most relevant information from the only context.
2. Generate a draft response using selected information.
3. Remove duplicate content from draft response.
4. Generate your final response after adjusting it to increase accuracy and relevance.
5. Only show your final response!

Constraints:
1. DO NOT PROVIDE ANY EXPLANATION OR DETAILS OR MENTION THAT YOU WERE GIVEN CONTEXT.
2. Don't mention that you are not able to find the answer in the provided context.
3. Don't make up the answers by yourself. Answer the question based on the below context.
4. Try your best to provide answer from the given context only.

{content}
"""

def process_query(query, collection_name):
    """
    Traite la requête de l'utilisateur en recherchant des documents similaires
    et en générant une réponse.

    Args:
        query (str): Requête de l'utilisateur.
        collection_name (str): Nom de la collection dans ChromaDB.

    Returns:
        str: Réponse finale générée pour la requête.
    """
    similarity_result = searchSimilarity(query, collection_name)
    answer = gradGeneration(similarity_result, query)
    return answer




# ------------------------------------------------------------------------------------------------------

def translation(texte,Langue): # function de traduction de texte qui retourne le texte traduit
    """
    Gère la traduction de texte

    Args:
        Prend le texte à traduire et la langue.

    Returns:
        str: retourne le texte traduit.
    """
    trad = GoogleTranslator(source='auto', target=Langue).translate(texte)
    return trad


def chatbotLLM(user_message, langueUser, max_new_tokens=50, do_sample=True, num_return_sequences=1, early_stopping=True):
    """
    Génère la réponse textuelle du chatbot

    Args:
        Prend la question de l'utilisateur et la langue.

    Returns:
        str: retourne la réponse du chatbot.
    """
    texteEntree = translation(user_message, "en")
    #result = generation_texte(texteEntree)

    # On génère entre le texte dans le model de chatbot:
    inputs = tokenizer.encode(texteEntree, return_tensors='pt')
    outputs = model.generate(
        inputs,
        max_new_tokens=max_new_tokens,
        do_sample=do_sample,
        num_return_sequences=num_return_sequences,
        early_stopping=early_stopping
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    texteSortie = result[len(texteEntree):].strip() # On récupère le résultat en anglais et on enlève la question.

    # texteSortie = result[0]["generated_text"] # On récupère la réponse du chatbot.

    if not langueUser == "en": # Si la langue de l'application n'ai pas l'anglais :
        texteSortie = translation(texteSortie,langueUser) # On traduit le texte dans la langue de l'utilisateur
    print(texteSortie)
    return texteSortie


