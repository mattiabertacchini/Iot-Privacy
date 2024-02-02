let map = null;
let previous_lat_long = null;
let greyIcon = null;
let redIcon = null;

$(document).ready(function () {
    $.ajax({
        url: '/shelves_dt',
        dataType: 'json',
        success: function (data) {
            // Initialize data table with JSON data

            $('#storage').DataTable({
                pageLength: 5,
                info: false,
                select: 'single',
                responsive: true,
                processing: true,
                // cursor: 'pointer',
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.12.1/i18n/it-IT.json'
                },
                dom: 'Bfrtip',
                columns: data.cols,
                data: data.shelves,
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

            //defnition of a marker (grey) for each shelf
            for (element of data.shelves) {
                var marker = L.marker([element['latitude'], element['longitude']], {icon: greyIcon}).addTo(map);
                marker.bindPopup(element['location']);
            }
        }
    });
});

//update map when click on a row
$('#storage').on('click', 'tbody tr', function () {
    let data = $('#storage').DataTable().row($(this)).data();
    map.panTo(new L.LatLng(data['latitude'], data['longitude']));
    let correct_lat_long;

    //setting red icon for current shelf selected
    map.eachLayer(function (layer) {
        if (layer instanceof L.Marker) {
            let current_lat_long = layer.getLatLng();
            if (current_lat_long == previous_lat_long) {
                layer.setIcon(greyIcon);
            } else if (current_lat_long.lat == data['latitude'] && current_lat_long.lng == data['longitude']) {
                layer.setIcon(redIcon);
                correct_lat_long = current_lat_long;
            }
        }
    });
    previous_lat_long = correct_lat_long;
});