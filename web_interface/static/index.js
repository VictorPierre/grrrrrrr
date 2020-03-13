$( document ).ready(function() {
    refresh();

    $("#reset_button").on('click', function() {
        refresh();
    });

    $("#submit_button").on('click', function() {
        $.ajax({
            type: "POST",
            url: "/submit",
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({ "moves": moves}),
            success : function(response, status){
                console.log(response);
                setTimeout(refresh, 1000);
            },
            error : function(response, status, error){
                console.log(error);
                console.log(response);
                setTimeout(refresh, 1000);
            }
        });
    });
});


var moves = []

var refresh = function(){
    $.ajax({
        type: "GET",
        url: "/load_map",
        success : function(response, status){
            $("#map").html(response);
            init_map();
            moves=[];
        },
        error : function(response, status, error){
            $("#map").html(response)
        }
    });
}

var init_map = function(){

    $('td').removeClass('selected');
    $('td').removeClass('suggested');
    $("td").unbind();
    $('#form').hide();
    
    $("td").on('click', function() {
        init_map()
    });

    $("."+specie).on('click', function() {
        $(this).addClass('selected');
        propose_moves(this);
    });
}

var reset_selection = function(){
    $('td').removeClass('selected');
    $('td').removeClass('suggested');
    $("td").unbind();
    $('#form').hide();
}

var propose_moves = function(element) {

    //initialisation de variables
    var n_cols = $(element).parent().children().length;
    var n_rows = $(element).parent().parent().children().length;
    var col = $(element).parent().children().index($(element));
    var row = $(element).parent().parent().children().index($(element).parent());
    var value = parseInt($(element).attr("value"))
    
    //Selection des cellules cibles
    allowed_cells = []
    for (i = Math.max(0, row-1); i < Math.min(n_rows, row+2); i++) {
        for (j = Math.max(0, col-1); j < Math.min(n_cols, col+2); j++) {
            if (i!=row || j!=col){
                allowed_cells.push($($(element).parent().parent().children()[i]).children()[j]);
            }
        }
    }

    //preparation des cellules cibles
    $(allowed_cells).addClass('suggested')
    $(allowed_cells).unbind()
    $('#nb_to_move').val(value);
    $('#form').show();
    
    $(allowed_cells).on('click', function() {
        move(this, element, parseInt($('#nb_to_move').val()))
    });
}

var move = function(target, source, n){
    var source_value = parseInt($(source).attr("value"))
    if (n<=source_value && n>0){
        //update source
        $(source).html(source_value-n)
        $(source).attr("value", source_value-n)

        //update target
        $(target).attr("moved", parseInt($(target).attr("moved"))+n)
        $(target).html($(target).attr("moved"))

        //update moves list
        var col_target = $(target).parent().children().index($(target));
        var row_target = $(target).parent().parent().children().index($(target).parent());
        var col_source = $(source).parent().children().index($(source));
        var row_source = $(source).parent().parent().children().index($(source).parent());
        moves.push([col_source, row_source, n, col_target, row_target])
    }
    init_map()
}