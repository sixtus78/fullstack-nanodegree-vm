jQuery(document).ready(function($) {

    /* notifications */
	$(document).on('click', '.notification > .delete', function() {
        $(this).parent().slideUp(400,function(){$(this).remove()});
        return false;
    });

});