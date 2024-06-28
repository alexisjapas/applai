import { resizeTextarea } from './autoresize.js'

document.addEventListener('DOMContentLoaded', () => {
    const applications = document.querySelectorAll('.application');
    const mainContent = document.getElementById('main');
    const popup = document.getElementById('application-popup');

    applications.forEach(application => {
        application.addEventListener('click', () => {
            // Get the ID of the clicked application
            const applicationId = application.id.split('-')[1];

            // Fetch application data from the server
            fetch(`/application/${applicationId}`)
                .then(response => response.json())
                .then(data => {

                    // Update the content of the popup
                    document.getElementById('application-title').innerText = data.job_title;
                    document.getElementById('application-company').innerText = data.company;
                    document.getElementById('application-recruiters').value = data.recruiters;
                    document.getElementById('application-cover_letter').value = data.cover_letter;
                    document.getElementById('popup-application-img').src = `${data.cover_letter_img}?t=${new Date().getTime()}`; // Set image source

                    // Show the popup and blur the background
                    popup.style.display = 'block';
                    mainContent.classList.add('blur-background');

                    // Ensure textareas in the popup are resized
                    const popupTextareas = popup.querySelectorAll('textarea');
                    popupTextareas.forEach(textarea => {
                        setupTextarea(textarea, applicationId);
                    });
                })
                .catch(error => console.error('Error fetching application data:', error));

            // Setup download button
            setupDownloadButton(applicationId)
        });
    });

    // Close popup function
    const closePopupButton = document.querySelector('.close-button');
    closePopupButton.addEventListener('click', () => {
        popup.style.display = 'none';
        mainContent.classList.remove('blur-background');
    });

    function setupDownloadButton(applicationId) {
        let button = document.getElementById("download-application");

        const oldButton = button.cloneNode(true);
        button.parentNode.replaceChild(oldButton, button);
        button = oldButton;

        const downloadApplication = () => {
            fetch(`/download_application/${applicationId}`, { method: 'GET' })
                .then(response => {
                    if (response.status === 200) {
                        return response.blob()
                    } else {
                        throw new Error(`Request failed with status ${response.status}`);
                    }
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `application_${applicationId}.pdf`; // Ensure the correct file extension
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        };

        button.addEventListener('click', downloadApplication)
    }

    function setupTextarea(textarea, applicationId) {
        // Remove any existing listeners to avoid duplication
        const oldTextarea = textarea.cloneNode(true);
        textarea.parentNode.replaceChild(oldTextarea, textarea);
        textarea = oldTextarea;

        const updateTextarea = () => {
            let formData = new FormData();
            formData.append((textarea.name.split('-')[1]), textarea.value)
            fetch(`/application/${applicationId}`, {
                method: 'POST',
                body: formData,
            })
                .then(response => {
                    if (response.status === 200) {
                        const popupApplicationImage = document.getElementById('popup-application-img');
                        const currentSource = popupApplicationImage.src.split('?')[0];
                        const newSource = `${currentSource}?t=${new Date().getTime()}`;
                        popupApplicationImage.src = newSource;
                        document.getElementById(`img-app-${applicationId}`).src = newSource;
                    }
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                })
                .catch(error => {
                    console.error('There was a problem while cover letter update:', error);
                });
        };

        resizeTextarea(textarea);
        textarea.addEventListener('input', updateTextarea);
    }
});