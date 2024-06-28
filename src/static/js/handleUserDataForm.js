import { resizeTextarea } from './autoresize.js'

// Selectors
const sections = [
    "links",
    "languages",
    "additional_skills",
    "educations",
    "experiences"
]

// Add event listeners to existing form fields
mapFormFieldsToDatabase();
hideDetailsSectionInputsIfEmpty();

// Set up autoresize on textareas
const textareas = document.querySelectorAll('textarea');
textareas.forEach(textarea => {
    textarea.removeEventListener('input', resizeTextarea);
    resizeTextarea(textarea);
});

sections.forEach((section) => {
    let sectionId = `${section}-section`
    let extraInputId = `${section}-extra_input`
    console.log(sectionId + " " + extraInputId)
    removeInputIfEmptyListener(document.getElementById(sectionId))
    handleExtraInputChanges(document.getElementById(sectionId), extraInputId);
})


function submitUserDataForm() {
    const formData = new FormData();
    const formFields = document.querySelectorAll('#user_data_form input, #user_data_form textarea');
    formFields.forEach(field => {
        if (field.name) {
            formData.append(field.name, field.value);
        }
    });
    fetch('/user', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function mapFormFieldsToDatabase() {
    const fields = document.querySelectorAll('#user_data_form input, #user_data_form textarea');
    fields.forEach(field => {
        field.removeEventListener('input', submitUserDataForm);
        field.addEventListener('input', submitUserDataForm);
    });
}

function removeInputIfEmptyListener(section){
    const sectionFields = Array.from(section.children)
    for (const elm of sectionFields) {
        elm.addEventListener(
            "keyup",
            function handleKeydownInFormFields() {
                if (elm.value.length == 0) {
                    elm.value = ""
                    elm.style.display = "none"
                    submitUserDataForm()
                }
            }
        )
    }
}

function handleExtraInputChanges(section, targetFieldId) {
    const targetField = document.getElementById(targetFieldId)
    
    //Section Listeners: hide or show section extra input depending on mouse hover the section
    const hideTargetFieldFunction = function hideTargetField() {
        targetField.style.display = "none";
    }
    const showTargetFieldFunction = function showTargetField() {
        targetField.style.display = "block";
    }

    section.addEventListener(
        "mouseenter",
        showTargetFieldFunction,
        false,
    );
    section.addEventListener(
        "mouseleave",
        hideTargetFieldFunction,
        false,
    );

    /*Extra Input Listener:
    * Link the extra input to the form if the user type in
    * Generate a new extra input, and remove specific listeners to the previous extra input (the previous extra input is now fully linked to the form)
    */
    targetField.addEventListener(
        "keydown",
        function handleKeydownInExtraInput(event) {
            if (!(event.key == "Backspace")) {

                // Link the extra input to the form if the user type in
                let previousInput = targetField.previousElementSibling
                let previousInputId = previousInput.id.split("-")
                let newInputId = String(parseInt(previousInputId[previousInputId.length - 1], 10) + 1) 
                if (isNaN(newInputId)) newInputId = 1
                const sectionIdPrefix = section.id.split('s-')[0];
                newInputId = sectionIdPrefix + "-" + newInputId
                targetField.id = newInputId
                targetField.name = newInputId
                let newTargetableField

                // Generate a new extra input, and remove specific listeners to the previous extra input (the previous extra input is now fully linked to the form)
                if (targetField.tagName == "INPUT") {
                    newTargetableField = document.createElement('input')
                    newTargetableField.setAttribute("type", "text")
                    newTargetableField.setAttribute("maxlenght", "255")
                } else if (targetField.tagName == "TEXTAREA") {
                    newTargetableField = document.createElement('textarea')
                    newTargetableField.setAttribute("maxlenght", "2000")
                    resizeTextarea(newTargetableField)
                }
                newTargetableField.setAttribute("id", targetFieldId)
                newTargetableField.setAttribute("name", targetFieldId)
                mapFormFieldsToDatabase()
                section.appendChild(newTargetableField)
                targetField.removeEventListener('keydown', handleKeydownInExtraInput);
                section.removeEventListener("mouseleave", hideTargetFieldFunction)
                section.removeEventListener("mouseenter", showTargetFieldFunction)
                handleExtraInputChanges(section, targetFieldId)
            }
        },
        false,
    );
}

// Hide empty details
function hideDetailsSectionInputsIfEmpty() {
    const section = document.getElementById('details-section');
    const inputs = section.querySelectorAll('input');

    section.addEventListener('mouseenter', () => {
        inputs.forEach(input => {
            if (input.value === '') {
                input.style.display = 'block';
            }
        });
    });

    section.addEventListener('mouseleave', () => {
        inputs.forEach(input => {
            if (input.value === '') {
                input.style.display = 'none';
            }
        });
    });

    inputs.forEach(input => {
        input.addEventListener('input', () => {
            if (input.value === '') {
                input.style.display = 'none';
            } else {
                input.style.display = 'block';
            }
        });
    });
}

// Set listeners on import/export buttons for user data form 
document.getElementById('export_button').addEventListener('click', function() {
    fetch('/export_user', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
            var downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", "user-data.json");
            document.body.appendChild(downloadAnchorNode); // required for firefox
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        });
});