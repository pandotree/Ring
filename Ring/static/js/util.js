//wtf does this do?
function handleAjaxError(jqXHR, textStatus, errorThrown){
    var e1 = 'Sorry! A server error occurred: "'+errorThrown+'".';
    if(confirm(e1+'\n\n'+'View error?')){
        win = window.open();
        win.document.write(jqXHR.responseText);
    }
}
