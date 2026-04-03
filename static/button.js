$(function() {
    $('#profile_button').on('click', function(e) {
    e.preventDefault()
    $.getJSON('/d_Func/profile_upload',
        function(data) {
        //do nothing
    });
    return false;
    });
});

$(function() {
    $('.add-member-button').on('click', function(e) {
    e.preventDefault()
    $.getJSON('/d_Func/add_member_button',
        function(data) {
        //do nothing
    });
    return false;
    });
});