user = {
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
};
