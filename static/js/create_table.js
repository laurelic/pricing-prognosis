var table = new Tabulator("#inpatient-table", {
    pagination: "local",
    paginationSize: 15,
    layout: "fitColumns",
    columns:[
        {title: "DRG Name", field: "drg_definition"},
        {title: "Prodiver ID", field: "provider_id"},
        {title: "Provider Name", field: "provider_name", headerFilter:true},
        {title: "Provider Address", field: "provider_street_address"},
        {title: "Provider City", field: "provider_city", headerFilter:true},
        {title: "Provider State", field: "provider_state", headerFilter:true},
        {title: "Provider Zip", field: "provider_zip_code", headerFilter:true},
        {title: "HRR Description", field: "hrr_description", headerFilter:true},
        {title: "Total Discharges", field: "total_discharges"},
        {title: "Avg Covered Charges", field: "average_covered_charges"},
        {title: "Avg Total Payments", field: "average_total_payments"}
    ],
});

$("#tabulator-controls button[name=download").on("click", function(){
    table.download("csv", "InpatientMedicareByHRR.csv")
})

d3.json("/inpatient_data", function(data) {
    table.setData(data);
});

// function fadeout() {
//     document.getElementById("loader").fadeou;
// }