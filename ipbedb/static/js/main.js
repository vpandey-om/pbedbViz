document.getElementById('genefile').addEventListener('change', getFile1)
function getFile1(event) {
	const input = event.target
	if ('files' in input && input.files.length > 0) {
			FileContent(input.files[0])
	}
}



function FileContent(file) {
	readFileContent(file).then(content => {
		console.log(content)
		// send content to server
		fetch(`${window.origin}/pbedb/getfiles`, {
    method: "POST",
    credentials: "include",
    body: JSON.stringify(content),
    cache: "no-cache",
    headers: new Headers({
      "content-type": "application/json"
    })
  })

  .then(function(response) {
    if (response.status !== 200) {
      console.log(`Looks like there was a problem. Status code: ${response.status}`);
      return;
    }
    response.json().then(function(data) {
      console.log(data);
    });
  })
  .catch(function(error) {
    console.log("Fetch error: " + error);
});


	}).catch(error => console.log(error))
}

function readFileContent(file) {
	const reader = new FileReader()
	return new Promise((resolve, reject) => {
		reader.onload = event => resolve(event.target.result)
		reader.onerror = error => reject(error)
		reader.readAsText(file)
	})
}


$(document).ready(function(){
var geneids=[];
var phenofigs=['fertility_fig_id','gam_fig_id','liver_fig_id','blood_fig_id'];
function loadGeneIds(){
	$.getJSON('/pbedb/get_pbanka_ids', function(data, status, xhr){

		for (var i = 0; i < data.length; i++ ) {
					// console.log(data[i]);
        	geneids.push(data[i]);
    	}

});
};

loadGeneIds();


$('#geneid').autocomplete({
	source: function(request, response) {
        var results = $.ui.autocomplete.filter(geneids, request.term);

        response(results.slice(0, 5));
    },
		messages: {
        noResults: 'no results',
        results: function(amount) {
            return amount + 'results.'
        }},
	});



	$("#gene_input_form").submit(function(event){
			event.preventDefault(); //prevent default action
			// console.log( $( this ).serializeArray() );
			// this is the single gene entry
			gene={
					gene:$('#geneid').val()
				},
			// this is the  gene list entry
			genelist={
						genelist:$('#genelist').val()
					},
			genefile={
			genefile:$('#genefile').val()
			},
			// get values form checkbox
			choices={
				// form-check-input is calss for java script
				choices:$('.form-check-input:checked').map(function() {return this.value;}).get().join(',')
			},


			// fig={
			// 		fig:$('#fertility_fig_id')
			// 	},

			// $.each( phenofigs, function( index, value ){
			// 	// var gd = document.getElementById(phenofigs[i])
			// 	// gd.data // => current data
			// 	// gd.layout // => current layout
			// 	var x=$(phenofigs[i])
			// 	// gd.data // => current data)
			// 	console.log(x)
			// });

			// console.log(choices)
			// // console.log(fig)
			//
			// /// redraw figure
			// var update = {
    	// opacity: 0.4,
    	// 'marker.color': 'red'
			// 	};
			// Plotly.restyle('fertility_fig_id', update);


			$.ajax({
					data: JSON.stringify([gene,genelist,genefile,choices]),
					type: 'POST',
					url : '/pbedb/process',
					contentType:'application/json',
					success: function(data) {

					var fig_pheno=JSON.parse(data.data)
					var all_pheno_fig=JSON.parse(data.all_pheno_fig)
					var fertility_fig=JSON.parse(data.fertility_fig)
					var gam_fig=JSON.parse(data.gam_fig)
					var blood_fig=JSON.parse(data.blood_fig)
					var liver_fig=JSON.parse(data.liver_fig)
					// var table=data.table_json

					// Plotly.newPlot('pheno_table',fig_pheno,{});
					Plotly.newPlot('fertility_fig_id', fertility_fig,{});
					Plotly.newPlot('all_pheno_fig_id', all_pheno_fig,{});
					Plotly.newPlot('gam_fig_id', gam_fig,{});
					Plotly.newPlot('liver_fig_id', liver_fig,{});
					Plotly.newPlot('blood_fig_id', blood_fig,{});

					//// create a table

					// var table = null;
					// if (table !== null) {
          //     table.destroy();
          //     table = null;
          //     $("#a_nice_table").empty();
          //   }
          //   $("#pheno_table_df").html(data.table);
          //   table = $("#a_nice_table").DataTable();
					$('#pheno_table_df').bootstrapTable('destroy')
						$('#pheno_table_df').bootstrapTable({
          data: data.table,
          columns: data.columns,
        });



					$.each( phenofigs, function( index, value ){



					myPlot2= document.getElementById(value);

					myPlot2.on('plotly_click', function(data){
						// this data is the point which was clicked
					console.log(data);
					 var gene = {
							name: data.points[0].text,
							};


							$.ajax({
								url: '/pbedb/get_clicked_gene',
								data: JSON.stringify(gene),
								type: 'POST',
								contentType:'application/json',
								// success: function(data1,data2,data3,data4) {
								success: function(data) {
									// console.log(data.data1);
									var all_combined_pheno_fig=JSON.parse(data.data)
									//
									Plotly.newPlot('all_pheno_fig_id',all_combined_pheno_fig,{});

									// console.log(data);
									// Plotly.newPlot('dendograph',graphs,{});
								},
								error: function(error) {
									console.log(error);
								}

							});



					});
						});

					// Plotly.newPlot('fertility_fig_id',fertility_fig,{});
					//
					// fertility_Plot = document.getElementById('fertility_fig_id');
					// // // console.log(graphs);
					// // // console.log(myPlot2);
					// //
					// fertility_Plot.on('plotly_click', function(data){
					// 	// this data is the point which was clicked
					// console.log(data);
					//  var gene = {
					// 		name: data.points[0].text,
					// 	};
					// });

																	},

					error: function(error) {
							console.log(error);
						},
				});
	});

// put clickable event
// $("#all_pheno_fig_id,#fertility_fig_id,#gam_fig_id").each(function(data){
// 	console.log(data)
//     // $(this).upload({
//     //     //whateveryouwant
//     // });
// });

$("#filter_input_form").submit(function(event){
		event.preventDefault(); //prevent default action
		// console.log( $( this ).serializeArray() );
		// this is the single gene entry
		male_ferti_gr={
				val:$('#male_ferti_gr').val()
			},
		male_ferti_le={
					val:$('#male_ferti_le').val()
				},

		female_ferti_gr={
				val:$('#female_ferti_gr').val()
			},
		female_ferti_le={
					val:$('#female_ferti_le').val()
				},

		male_gam_gr={
				val:$('#male_gam_gr').val()
			},
		male_gam_le={
					val:$('#male_gam_le').val()
				},

		female_gam_gr={
				val:$('#female_gam_gr').val()
			},
		female_gam_le={
					val:$('#female_gam_le').val()
				},
		blood_gr={
				val:$('#blood_gr').val()
			},
		blood_le={
					val:$('#blood_le').val()
				},
		liver_gr={
						val:$('#liver_gr').val()
					},
		liver_le={
							val:$('#liver_le').val()
						},

	content=[male_ferti_gr,male_ferti_le,female_ferti_gr,female_ferti_le,male_gam_gr,male_gam_le,female_gam_gr,female_gam_le,blood_gr,blood_le,liver_gr,liver_le]

			$.ajax({
				url: '/pbedb/get_filter_form_values',
				data: JSON.stringify(content),
				type: 'POST',
				contentType:'application/json',
				// success: function(data1,data2,data3,data4) {
				success: function(data) {
						var all_pheno_fig=JSON.parse(data.all_pheno_fig)
						var fertility_fig=JSON.parse(data.fertility_fig)
						var gam_fig=JSON.parse(data.gam_fig)
						var blood_fig=JSON.parse(data.blood_fig)
						var liver_fig=JSON.parse(data.liver_fig)
						// var table=data.table_json

						Plotly.newPlot('fertility_fig_id', fertility_fig,{});
						Plotly.newPlot('all_pheno_fig_id', all_pheno_fig,{});
						Plotly.newPlot('gam_fig_id', gam_fig,{});
						Plotly.newPlot('liver_fig_id', liver_fig,{});
						Plotly.newPlot('blood_fig_id', blood_fig,{});

						$('#pheno_table_df').bootstrapTable('destroy')
							$('#pheno_table_df').bootstrapTable({
						data: data.table,
						columns: data.columns,
					});

					/// now we would like add click event

					$.each( phenofigs, function( index, value ){

					myPlot2= document.getElementById(value);

					myPlot2.on('plotly_click', function(data){
						// this data is the point which was clicked
					console.log(data);
					 var gene = {
							name: data.points[0].text,
							};


							$.ajax({
								url: '/pbedb/get_clicked_gene',
								data: JSON.stringify(gene),
								type: 'POST',
								contentType:'application/json',
								// success: function(data1,data2,data3,data4) {
								success: function(data) {
									// console.log(data.data1);
									var all_combined_pheno_fig=JSON.parse(data.data)
									//
									Plotly.newPlot('all_pheno_fig_id',all_combined_pheno_fig,{});

									// console.log(data);
									// Plotly.newPlot('dendograph',graphs,{});
								},
								error: function(error) {
									console.log(error);
								}

							});
						});


				// },
				// error: function(error) {
				// 	console.log(error);
				// }

			});



				},
				error: function(error) {
					console.log(error);
				}

			});

		})


// we are going to download_data

$( "#download_button" ).click(function() {
  // alert( "Handler for .click() called." );
	// ajax call
	var gene = {};
	$.ajax({

		url: '/pbedb/download_data',
		data: JSON.stringify(gene),
		type: 'POST',
		contentType:'application/json',
		// success: function(data1,data2,data3,data4) {
		success: function(data) {
			console.log(data.page);
			window.location.href=data.page;
			// console.log(data.data1);
			// var all_combined_pheno_fig=JSON.parse(data.data)
			// //
			// Plotly.newPlot('all_pheno_fig_id',all_combined_pheno_fig,{});

			// console.log(data);
			// Plotly.newPlot('dendograph',graphs,{});
		},
		error: function(error) {
			console.log(error);
		}

	});
});


}); ///end of document ready





// get clicked gene Id by javascript
function getGeneID(s)
{
	fertility_Plot = document.getElementById(s);
	// // console.log(graphs);
	// // console.log(myPlot2);
	//
	fertility_Plot.on('plotly_click', function(data){
		// this data is the point which was clicked

	 var gene = {
			name: data.points[0].text,
		};
		console.log(gene);
		// send content to server
				fetch(`${window.origin}/pbedb/get_clicked_gene`, {
		    method: "POST",
		    credentials: "include",
		    body: JSON.stringify(gene),
		    cache: "no-cache",
		    headers: new Headers({
		      "content-type": "application/json"
		    })
		  })

		  .then(function(response) {
		    if (response.status !== 200) {
		      console.log(`Looks like there was a problem. Status code: ${response.status}`);
		      return;
		    }
		    response.json().then(function(data) {
		      //console.log(data);
					var all_combined_pheno_fig=JSON.parse(data.data)
					//
					Plotly.newPlot('all_pheno_fig_id',all_combined_pheno_fig,{});
					/// here we replot the graph
		    });
		  })
		  .catch(function(error) {
		    console.log("Fetch error: " + error);
		});

	});


}

var phenofigs=['fertility_fig_id','gam_fig_id','liver_fig_id','blood_fig_id'];
var i;


for (i = 0; i < phenofigs.length; i++) {
	// console.log(i)
  getGeneID(phenofigs[i])
}

// fetch  values from the filter form

// function download_table()
// {
// 	var content={};
// 	console.log(content)
// 	fetch(`${window.origin}/pbedb/download_data`, {
// 	method: "POST",
// 	credentials: "include",
// 	body: JSON.stringify(content),
// 	cache: "no-cache",
// 	headers: new Headers({
// 		"content-type": "application/json"
// 	})
// 	})
//
// 	.then(function(response) {
// 	if (response.status !== 200) {
// 		console.log(`Looks like there was a problem. Status code: ${response.status}`);
// 		return;
// 	}
// 	response.json().then(function(data) {
// 		// console.log(data);
// 	});
// 	})
// 	.catch(function(error) {
// 	console.log("Fetch error: " + error);
// 	});
//
//
// }
//
// document.getElementById("download_button").onclick = function() {download_table()};


// Javascript for download button

// function filter_form_submit_by_id() {
//
//
//
//
// // for male fertility
// var male_ferti_gr = document.getElementById("male_ferti_gr").value;
// var male_ferti_le = document.getElementById("male_ferti_le").value;
// // for female fertility
//
// var female_ferti_gr = document.getElementById("female_ferti_gr").value;
// var female_ferti_le = document.getElementById("female_ferti_le").value;
//
// // for male gametocytes
// var male_gam_gr = document.getElementById("male_gam_gr").value;
// var male_gam_le = document.getElementById("male_gam_le").value;
//
// // for eachmale gametocytes
// var female_gam_gr = document.getElementById("female_gam_gr").value;
// var female_gam_le = document.getElementById("female_gam_le").value;
//
// // for blood phenoype
// var blood_gr = document.getElementById("blood_gr").value;
// var blood_le = document.getElementById("blood_le").value;
//
// // for liver phenoype
// var liver_gr = document.getElementById("liver_gr").value;
// var liver_le = document.getElementById("liver_le").value;
//
// content=[male_ferti_gr,male_ferti_le,female_ferti_gr,female_ferti_le,male_gam_gr,male_gam_le,female_gam_gr,female_gam_le,blood_gr,blood_le,liver_gr,liver_le]
//
//
//
// // send content to server
// 		fetch(`${window.origin}/pbedb/get_filter_form_values`, {
// 		method: "POST",
// 		credentials: "include",
// 		body: JSON.stringify(content),
// 		cache: "no-cache",
// 		headers: new Headers({
// 			"content-type": "application/json"
// 		})
// 	})
// 	.then(function(response) {
// 		if (response.status !== 200) {
// 			console.log(`Looks like there was a problem. Status code: ${response.status}`);
// 			return;
// 		}
// 		response.json().then(function(data) {
// 			console.log(data);
// 		// 	var all_pheno_fig=JSON.parse(data.all_pheno_fig)
// 		// 	var fertility_fig=JSON.parse(data.fertility_fig)
// 		// 	var gam_fig=JSON.parse(data.gam_fig)
// 		// 	var blood_fig=JSON.parse(data.blood_fig)
// 		// 	var liver_fig=JSON.parse(data.liver_fig)
// 		// 	// var table=data.table_json
// 		//
// 		// 	Plotly.newPlot('fertility_fig_id', fertility_fig,{});
// 		// 	Plotly.newPlot('all_pheno_fig_id', all_pheno_fig,{});
// 		// 	Plotly.newPlot('gam_fig_id', gam_fig,{});
// 		// 	Plotly.newPlot('liver_fig_id', liver_fig,{});
// 		// 	Plotly.newPlot('blood_fig_id', blood_fig,{});
// 		//
// 		// 	$('#pheno_table_df').bootstrapTable('destroy')
// 		// 		$('#pheno_table_df').bootstrapTable({
// 		// 	data: data.table,
// 		// 	columns: data.columns,
// 		// });
//
// 		});
// 	})
// 	.catch(function(error) {
// 		console.log("Fetch error: " + error);
// });
//



//
// }

// document.getElementById("filter_input_form").submit();



// var gd = document.getElementById('fertility_fig_id')
//
// gd.data // => current data
// gd.layout // => current layout
// console.log(gd.data)


	// $("#gene_input_form").on('click', '#geneid', function () {
	// 		entry={
	// 				gene:$('#single_gene').val()
	// 			}
	// 		$.ajax({
	// 				data: JSON.stringify(entry),
	// 				type: 'POST',
	// 				url : '/pbedb/process',
	// 				contentType:'application/json',
	// 				success: function(data) {
	// 								var g = JSON.parse(data.gene);
	// 								// $('#result').html(g).show();
	// 								console.log(g);
	// 																},
	// 				error: function(error) {
	// 						console.log(error);
	// 					},
	// 			});
	// });








				// $("#geneid").autocomplete({
				//         source: geneids,
				//         minLength: 1,
				//         select: function (event, ui) {
				//             // feed hidden id field
				//             $("#field_id").val(ui.item.id);
				//             // update number of returned rows
				//             $('#results_count').html('');
				//         },
				//         open: function (event, ui) {
				//             // update number of returned rows
				//             var len = $('.ui-autocomplete > li').length;
				//             $('#results_count').html('(#' + len + ')');
				//         },
				//         close: function (event, ui) {
				//             // update number of returned rows
				//             $('#results_count').html('');
				//         },
				//         // mustMatch implementation
				//         change: function (event, ui) {
				//             if (ui.item === null) {
				//                 $(this).val('');
				//                 $('#field_id').val('');
				//             }
				//         }
				//     });
				//
				//     // mustMatch (no value) implementation
				//     $("#field").focusout(function () {
				//         if ($("#field").val() === '') {
				//             $('#field_id').val('');
				//         }
				//     });
				//



	// $("#gene_input_form").on('click', '#geneid', function () {
	// 		entry={
	// 				gene:$('#single_gene').val()
	// 			}
	// 		$.ajax({
	// 				data: JSON.stringify(entry),
	// 				type: 'POST',
	// 				url : '/pbedb/process',
	// 				contentType:'application/json',
	// 				success: function(data) {
	// 								var g = JSON.parse(data.gene);
	// 								// $('#result').html(g).show();
	// 								console.log(g);
	// 																},
	// 				error: function(error) {
	// 						console.log(error);
	// 					},
	// 			});
	// });


	// Getter



// document.getElementById('genefile').addEventListener('change', getFile)

	// function getFile(event) {
	// 	const input = event.target
	// 	if ('files' in input && input.files.length > 0) {
	// 		placeFileContent(
	// 			document.getElementById('genelist'),
	// 			input.files[0])
	// 	}
	// }
	//
	// function placeFileContent(target, file) {
	// 	readFileContent(file).then(content => {
	// 		target.value = content
	// 			console.log(target.value)
	// 	}).catch(error => console.log(error))
	// }


	// console.log($('#genefile'));
