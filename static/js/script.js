let mydomorigin = window.location.origin; 

function chatbot() {
    let url = mydomorigin + '/chatbotGpt2/' // récupère l'url de la views validationCart dans urls.py

    // var message = $('#userinput').val();
    message = document.getElementById('userinput').value 


    if (message.trim() === '') { // trim = remplace les espaces de la chaine de caractère avant et après par ""
        return;
    }


    
    $('#chat-log').append('<div class="alert alert-light" role="alert">'+message+'</div>');
    $('#chat-log').append('<div class="spinner-border text-primary" role="status"></div>');
    
    $('#userinput').val(''); 

    var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value; // On récupère le csrf de la page paiement.html

    
    $.ajax({
        url: url,
        type: 'POST', //url: '{% url "chatbotGpt2" %}', 
        dataType: "json", // Type clé valeurs exemple nom:Boudjidj ; prénom:Bilal de format à envoyer
        data: {
            message: message,
            csrfmiddlewaretoken: csrf_token,
        },
        success: function(response) {
            $('#chat-log').append('<div class="alert alert-info" role="alert">Bot : '+ response.response +'</div>'); 
            const element = document.querySelector(".spinner-border");
            element.remove(); // supprime le div avec l'identifiant 'div-02'
        },
        error: function() {
            $('#chat-log').append('<div class="alert alert-danger" role="alert">Bot : An error occurred.</div>');
            const element = document.querySelector(".spinner-border");
            element.remove(); // supprime le div avec l'identifiant 'div-02'
        }
    });
}