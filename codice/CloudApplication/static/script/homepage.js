/**
 * Al caricamento della pagina faccio una chiamata per ottenere i prodotti esistenti e rimepire la select prodotto.
 */




let map = null;
let previous_lat_long = null;
let greyIcon = null;
let redIcon = null;

$(document).ready(function () {

    $.ajax({

        url: '/get_all_products',
        dataType: 'json',

        success: function (data) {

            var selectElement = document.getElementById("product")

            for (var i = 0; i < data.length; i++) {
                var option = document.createElement("option");
                option.value = data[i]["product_id"];
                option.text = data[i]["product_description"];
                selectElement.add(option);
            }

        }


    })


    //map initialization
    greyIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-grey.png'
    });
    redIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png'
    });
    map = L.map('map').setView([44.64791785334392, 10.921045454551434], 13);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);


})

$('#product').on('change', function () {

    map.eachLayer(function (layer) {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer)
        }
    })

    var selectElement = document.getElementById("location")
    selectElement.innerHTML = '';
    var option = document.createElement("option");
    option.text = "Seleziona"
    selectElement.add(option)

    var dataAjax = new FormData()
    dataAjax.append('product_id', $('#product').val())
    $.ajax({

        url: '/get_all_locations',
        dataType: 'json',
        data: dataAjax,
        type: 'POST',
        contentType: false,
        cache: false,
        processData: false,

        success: function (data) {

            selectElement.disabled = false;

            for (var i = 0; i < data.length; i++) {
                var option = document.createElement("option");
                option.value = data[i]['shelf_id'];
                option.text = data[i]['location'];
                option.setAttribute('data-lat', data[i]['latitude'].toString());
                option.setAttribute('data-long', data[i]['longitude'].toString());

                selectElement.add(option);
                //defnition of a marker (grey) for each shelf
                var marker = L.marker([data[i]['latitude'].toString(), data[i]['longitude'].toString()], {icon: greyIcon}).addTo(map);
                marker.bindPopup(data[i]['location']);
            }

        }


    })

})

$('#location').on('change', function () {

    let datalat = parseFloat(this.options[this.selectedIndex].getAttribute('data-lat'));
    let datalong = parseFloat(this.options[this.selectedIndex].getAttribute('data-long'));
    map.panTo(new L.LatLng(datalat, datalong));
    let correct_lat_long;

    //setting red icon for current shelf selected
    map.eachLayer(function (layer) {
        if (layer instanceof L.Marker) {
            let current_lat_long = layer.getLatLng();
            if (current_lat_long == previous_lat_long) {
                layer.setIcon(greyIcon);
            } else if (current_lat_long.lat == datalat && current_lat_long.lng == datalong) {
                layer.setIcon(redIcon);
                correct_lat_long = current_lat_long;
            }
        }
    });
    previous_lat_long = correct_lat_long;
});

$('#formPrediction').on('submit', function (e) {
        e.preventDefault();
        // librerie da guardare:
        // - swal (sweetalert) per l'avviso.
        // - selectpicker
        if (true) {

            var dataAjax = new FormData();
            dataAjax.append('datetime_str', $('#data_ora').val())
            dataAjax.append('shelf_id', $('#location').val())

            $.ajax({

                url: '/predict_shelf',
                dataType: 'json',
                data: dataAjax,
                type: 'POST',
                contentType: false,
                cache: false,
                processData: false,

                success: function (data) {

                    map.eachLayer(function (layer) {
                        if (layer instanceof L.Marker) {
                            if (layer.options.icon == redIcon) {
                                layer.setPopupContent("Il prodotto selezionato sarà disponibile in quantità (" + data['yhat'].toFixed(0) + ") per il giorno (" + data['ds'] + ")")
                                layer.openPopup();
                            }
                        }
                    });
                }
            })
        }

    }
)
