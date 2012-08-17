/*

PLEASE USE THIS JAVASCRIPT CLICK FUNCTION AS A MODEL FOR FUTURE AJAX CALLS
$('#login-user-submit').click(function () {

        var url = '/login/';
        console.debug($('#login-user-form').serialize());
        console.debug("trying to log in");

        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'html',
            data: $('#login-user-form').serialize(),
            complete: function(xhr, textStatus) {
                
            },
            success: function(data) {
                document.write(data);
            },
            error: function(xhr, textStatus, errorThrown){
                console.debug(errorThrown);
                console.debug(textStatus);
                console.debug(xhr);
                var e1 = 'Sorry! A server error occurred: \"'+errorThrown+'\"\.';
                if(confirm(e1+'\n\n'+'View error?')){
                    win = window.open();
                    win.document.write(xhr.responseText);
                }
            },
        });
    });
*/