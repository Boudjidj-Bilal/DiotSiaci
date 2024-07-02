document.addEventListener('DOMContentLoaded', function () {
    const spinner = document.getElementById('upload-spinner');
    const message = document.getElementById('upload-message');
    const uploadform = document.getElementById('upload-form');
    const filerreur = document.getElementById('file-error');
    const uploadfiles = document.getElementById('files');


    let mydomorigin = window.location.origin; 
    url = mydomorigin + '/upload/';

    document.getElementById('upload-form').addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = new FormData();
        const files = uploadfiles.files;

        // Validate file extensions
        const allowedExtensions = ['pdf', 'txt'];
        let validFiles = true;
        Array.from(files).forEach(file => {
            if (!allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
                filerreur.innerText = `Format de fichier invalide: ${file.name}. Seulement les fichiers PDF et TXT sont permis.`;
                validFiles = false;
            }
        });

        if (!validFiles) {
            return;
        }

        // Add files to FormData
        for (let i = 0; i < files.length; i++) {
            formData.append('documents', files[i]);
        }


        spinner.style.display = 'inline'; // Afficher le spinner
        message.innerHTML = '';

        // Submit form via AJAX
        fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("La communication réseau n'est pas disponible");
                }
                return response.json();

            })
            .then(data => {
                message.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                uploadform.reset(); // Clear form after successful upload
                filerreur.innerText = ''; // Clear any previous error messages
                spinner.style.display = 'none'; // Afficher le spinner

            })
            .catch(error => {
                console.error('Error:', error);
                spinner.style.display = 'none'; // Cacher le spinner
                message.innerHTML = `<div class="alert alert-danger">Erreur de téléversement de fichiers</div>`;
            });
    });

});