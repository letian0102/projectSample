function high_contrast() {
    var b = document.body;

    if(b.classList.contains('hc-mode')){
        b.classList.remove('hc-mode');
        localStorage.setItem('hc-Mode', 'disabled');
    }
    else
    {
        b.classList.add('hc-mode');
        localStorage.setItem('hc-Mode', 'enabled');
    }
};

if(localStorage.getItem('hc-Mode') == 'enabled'){
    document.body.classList.add('hc-mode');
    
}
else
{
    document.body.classList.add('non-hc-mode');
};