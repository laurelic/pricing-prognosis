// add the first entry of all dropdown
function selectOne(selector){
	selector
		.append("option")
		.text("Select One");
}

// initial load of drg dropdown
d3.json("/drg_all").then(function(data) {
	var selector = d3.select("#selDrgDataset");
	// console.log(data);
	selectOne(selector);
	data.forEach(function(d) {
		selector
			.append("option")
			.text(d['drg_definition'])
			.property("value", d['drg_id'] + '|'+ d['weights'] + '|' + d['geometric_mean_los'] + '|' + d['arithmetic_mean_los'] + '|' + d['drg_definition']);
	});
	const firstSample = data[0];
});

// initial load of hrr dropdown
d3.json("/hrr_all").then(function(data) {
	var selector = d3.select("#selHrrDataset");
	// console.log(data);
	selectOne(selector);
	data.forEach(function(d) {
		selector
			.append("option")
			.text(d['hrr_description'])
			.property("value", d['hrr_id'] + '|' + d['hrr_description']);
	});
	const firstSample = data[0];
}); 

// initial load of provider dropdown
d3.json("/provider_all").then(function(data) {
	var selector = d3.select("#selProviderDataset");
	selectOne(selector);
	data.forEach(function(d) {
		selector
			.append("option")
			.text(d['provider_name'])
			.property("value", d['provider_rowid'] + '|' + d['provider_name']);
	});
	const firstSample = data[0];

}); 


// relod hrr dropdown content, based on the selected drg
// only populated with hrr that has had the selected drg
function hrrReload( drg_definition ){
	// console.log("reload Hrr function: " + drg_definition);
	// clear existing options before reload
	document.getElementById("selHrrDataset").options.length = 0;
	
	var path = "/hrr/" + drg_definition;
	// console.log ("hrr path: " + path);
	
	d3.json(path).then(function(data) {
	var selector = d3.select("#selHrrDataset");
	// console.log(data);
	selectOne(selector);
	data.forEach(function(d) {
		selector
			.append("option")
			.text(d['hrr_description'])
			.property("value", d['hrr_id'] + '|' + d['hrr_description'] + '|' + drg_definition );
	});
	const firstSample = data[0];
}); 

};


// load providers with in the selected drg/hrr  
function providerHrrReload( drg_definition, hrr_description ){
	// console.log("reload providerHrrReload function: " + drg_definition + ' ' + hrr_description);

	// clear existing options before reload
	document.getElementById("selProviderDataset").options.length = 0;
	
	var drg_hrr = drg_definition + '|' + hrr_description
	var path = "/hrrprovider/" + drg_hrr;
	// console.log (path);
	
	d3.json(path).then(function(data) {
		// console.log("json call");
		var selector = d3.select("#selProviderDataset");
		selectOne(selector);
		data.forEach(function(d) {
			selector
				.append("option")
				.text(d['provider_name'])
				.property("value", d['provider_rowid'] + '|' + d['provider_name']);
		});
		const firstSample = data[0];

	})
};


function drgOptionChanged(newSample) {
	var drg_sel = newSample;
	// console.log('drg: ' + drg_sel);
	var drg_arr = drg_sel.split("|");
	var drg_definition = drg_arr[4];
	// console.log('drg_definition: '  + drg_definition);
	// reload hrr list to contain only hrr that performed the procedure
	hrrReload (drg_definition);

};

function hrrOptionChanged(newSample) {
	var hrr_sel = newSample;
	// console.log ('hrr: ' + hrr_sel);
	var hrr_arr = hrr_sel.split("|");
	// console.log('hrr_description: ' + hrr_arr[1]);
	var hrr_description = hrr_arr[1];
	var drg_definition = hrr_arr[2];
	//load providers with in the selected drg/hrr  
	providerHrrReload (drg_definition, hrr_description);
	// console.log("reload provider");
};

function providerOptionChanged(newSample) {
	var provider_sel = newSample;
	// console.log('provider: ' + provider_sel);
};