

$(document).ready(function () {
    // sorting della colonna date time all'interno della datatable
    $.fn.dataTable.moment('DD/MM/YYYY HH:mm:ss');
    // Esegui una chiamata AJAX per ottenere il file JSON
    $.ajax({
        url: '/history_dt', // URL del tuo file JSON
        dataType: 'json',
        success: function (data) {
            // Popola la DataTable con i dati JSON

            $('#history').DataTable({
                columnDefs: [
                    {
                        target: 2,
                        visible: false
                    },
                    {
                        target: 4,
                        visible: false
                    }
                ],
                info: false, // toglie il footer dalla DataTable 'Selezionate x linee…'
                select: 'single',
                responsive: true,
                processing: true,

                // cursor: 'pointer',
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.12.1/i18n/it-IT.json'
                },
                dom: 'Bfrtip',
                columns: data.cols,
                data: data.movements,
            })
        }
    });
});