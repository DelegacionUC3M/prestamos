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

function dropDown(option) {
    if (option == 0) {
        // Muestra las opciones de los objetos
        document.getElementById("dropdown_objects").classList.toggle("show");
    } else if (option == 1){
        // Muestra las opciones de los prestamos
        document.getElementById("dropdown_loans").classList.toggle("show");
    } else if (option == 2) {
        // Muestra las opciones de las sanciones
        document.getElementById("dropdown_penalties").classList.toggle("show");
    }
}

// Si se pulsa fuera del boton se cierra el dropdown
window.onclick = function(event) {
    if (!event.target.matches('.dropdownbtn')) {

        // Obtenemos el dropdown con mas opciones
        var dropdowns = document.getElementsByClassName("dropdown_objects");
        var i;
        for (i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}
