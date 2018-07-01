 /* Busca en la tabla el campo seleccionado*/
 /* Para hacer la busqueda case sensitive, eliminar toUpperCase*/
function searchItem() {
// Declare variables
    var input, filter, ul, li, a, i, text;
    input = document.getElementById('Buscador');
    filter = input.value.toUpperCase();
    ul = document.getElementById("objetos");
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        text = a.innerHTML.toUpperCase()
        if (text.indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
