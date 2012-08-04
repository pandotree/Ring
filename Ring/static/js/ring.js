user = {
    /*
     TODO: decouple these methods and classes from the templates that are calling them. EX:

    $('#BUTTON_NUM').click(function() {

        $.ajax('/create_user/',{
            type: 'post',
            data: query,
            dataType: 'json',
            success: function(data){
                //ACTIONS?
            },
            error: handleAjaxError,
        });
    })
    */

    createUser: function(query){
        var ok = false; 

        $.ajax('/create_user/',{
            type: 'post',
            data: query,
            dataType: 'json',
            success: function(data){
                ok = true;
            },
            error: handleAjaxError,
        });
        return ok;
    },

    loginUser: function(query){
        var ok = false;
        console.debug("trying to log in");

        $.ajax('/login/', {
            type: 'post',
            data: query,
            dataType: 'json',
            success: function(data){
                console.debug("logged in");
                ok=true;
            },
            error: handleAjaxError,
        });
        return ok;
    },
};

group = {
    createGroup: function(query){
        var ok = false; 

        $.ajax('/create_group/',{
            type: 'post',
            data: query,
            dataType: 'json',
            success: function(data){
                ok = true;
            },
            error: handleAjaxError,
        });
        return ok;
    },
};