/* Busca en la tabla el campo seleccionado*/
/* Para hacer la busqueda case sensitive, eliminar toUpperCase*/
function searchItem() {
    var input, filter, table, tr, td, i, select;
    input = document.getElementById("Buscador");
    filter = input.value.toUpperCase();
    table = document.getElementById("Tabla");
    tr = table.getElementsByTagName("tr");
    select = document.getElementById("Opciones");

    if (!select){
        option = 0;
    }
    // Obtiene el valor del selector
    var option = select.options[select.selectedIndex].value;
    // Itera sobre los las filas y oculta los elementos que no cumples la búsqueda
    for (i = 0; i < tr.length; i++) {
        // Busca en la colummna elegida en el selector
        td = tr[i].getElementsByTagName("td")[option];
        if (td) {
            if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

function fillForm(id) {
    var table = document.getElementsByTagName("table")
    var rows = table[0].rows
    var cols = rows[id].getElementsByTagName("td");

    document.getElementById("form_name").value = cols[1].innerHTML;
    document.getElementById("form_amount").value = cols[2].innerHTML;
    document.getElementById("form_type").value = cols[3].innerHTML;
    document.getElementById("form_state").value = cols[4].innerHTML;
    document.getElementById("form_days").value = cols[5].innerHTML;
    document.getElementById("form_penalty").value = cols[6].innerHTML;
    
}

// Las fechas son las del dia actual
window.onload = function() {
    document.getElementById("form_date").value = new Date().toISOString().substring(0, 10)
}

$(window).on('load', function(){
    $('#errorModal').modal({show:true})
})
