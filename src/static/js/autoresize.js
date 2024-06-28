export function resizeTextarea(textarea) {
    const resizeTextarea = () => {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    };

    textarea.addEventListener('input', resizeTextarea);

    // Initialize the height based on the initial content
    resizeTextarea();
}
