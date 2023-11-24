localStorage.setItem(1, "15m");
localStorage.setItem(0, "15m");

$(document).ready(function(){

    $("#btn_predict").click(function(){
        var txt_data = $('#txt_field').val();
        $.ajax({
           type: 'post',
           async: true,
           data: {data:txt_data},
           beforeSend: function (xhr) {
                $('.overlay').show();
                $('#searching-loader').show();
            },
            success: function (data) {
              $('#searching-loader').hide();
            }
        });
    });

    $("#btn_dashboard").click(function(){
        $.ajax({
           type: 'post',
           async: true,
           beforeSend: function (xhr) {
                $('.overlay').show();
                $('#searching-loader').show();
            },
            success: function (data) {
              $('#searching-loader').hide();
            }
        });
    });

    $("#btn_multiple_threads").click(function(){
        $.ajax({
           type: 'post',
           async: true,
           beforeSend: function (xhr) {
                $('.overlay').show();
                $('#searching-loader').show();
            },
            success: function (data) {
              $('#searching-loader').hide();
            }
        });
    });
});