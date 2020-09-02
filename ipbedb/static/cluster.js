
myPlot = document.getElementById('bargraph');
myPlot.on('plotly_click', function(data){
  // this data is the point which was clicked
// console.log(data.points[0].data.text);
var entry = {
    name: data.points[0].data.text,
    };


    $.ajax({
      url: '/clustergeneClick',
      data: JSON.stringify(entry),
      type: 'POST',
      contentType:'application/json',
      success: function(data) {
        var graphs = JSON.parse(data)
        // console.log(graphs);
        Plotly.newPlot('dendograph',graphs,{});
      },
      error: function(error) {
        console.log(error);
      }
      // .done(function(data) {
      // // Plotly.plot('dendograph',data,{});
      // console.log(data);

      // }
    });

//
// java acript for  sending data to routes
// fetch(`${window.origin}/cluster/get_cluster`, {
// fetch(`${window.origin}/dendogram`, {
//     method: "POST",
//     credentials: "include",
//     body: JSON.stringify(entry),
//     cache: "no-cache",
//     headers: new Headers({
//       "content-type": "application/json"
//     })
//     })
  //   .then(function (response) {
  //     if (response.status !== 200) {
  //       console.log(`Looks like there was a problem. Status code: ${response.status}`);
  //       return;
  //     }
  //     response.json().then(function (data) {
  //     console.log(data);
  //   });
  // })
  // .catch(function (error) {
  //   console.log("Fetch error: " + error);
  // });

});
