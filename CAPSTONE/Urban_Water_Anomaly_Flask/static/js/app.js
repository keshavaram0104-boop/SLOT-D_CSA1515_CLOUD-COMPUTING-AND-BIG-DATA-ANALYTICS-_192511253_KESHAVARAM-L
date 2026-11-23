function drawDashboard(byLocation, normal, anomalies){
 const loc=document.getElementById('locationChart');
 if(loc) new Chart(loc,{type:'bar',data:{labels:Object.keys(byLocation),datasets:[{label:'Average litres',data:Object.values(byLocation),backgroundColor:'#1d91a8',borderRadius:7}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,grid:{color:'#edf1f5'}},x:{grid:{display:false}}}}});
 const st=document.getElementById('statusChart');
 if(st) new Chart(st,{type:'doughnut',data:{labels:['Normal','Anomaly'],datasets:[{data:[normal,anomalies],backgroundColor:['#20a47a','#e66b65'],borderWidth:0}]},options:{responsive:true,cutout:'70%',plugins:{legend:{position:'bottom'}}}});
}
