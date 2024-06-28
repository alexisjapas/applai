function displayApplicationGenerationWaitingScreen(){
    let index = 1;
    const loading_texts = ['Work in progress', 'Work in progress.', 'Work in progress..', 'Work in progress...',];
    const loading_screen = document.getElementById('loading_screen');
    loading_screen.style.visibility = 'visible';
    setInterval(() => {
        loading_screen.innerText = loading_texts[index];
        index = (index + 1) % (loading_texts.length);
    }, 1000);
}