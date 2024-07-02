from django.urls import path 

from main import views
app_name = "appMain"


urlpatterns = [
    path('',views.mainViews,name='pageMain'),
    path('article/<int:articleId>/',views.article,name='pageArticle'),
    path('change-language/<str:language_code>/', views.change_language, name='change_language'),
    path('chatbotGpt2/', views.chatbotGpt2, name='chatbotGpt2'),
    path('chatbotRag/', views.chatbotRag, name='chatbotRag'),  # URL vers la vue chatbot
    path('upload/', views.upload_files, name='upload_files'),
]