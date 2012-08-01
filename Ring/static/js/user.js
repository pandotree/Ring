user = {
    // default: first create a user

    createUser: function(query){
        var ok = false;

        console.debug(1);
        console.debug(query);

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
