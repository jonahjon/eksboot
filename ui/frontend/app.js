'use strict';

// the control plane proxy URL:
var cpURL = 'http://localhost:8080';

// how fast to refresh cluster list (5 * 60 * 1000 = every 5 min)
var refreshClusterList= 120*1000;

// how fast to refresh cluster details (1* 1000 = every second)
var refreshClusterDetails = 60*1000;

$(document).ready(function($){
  clusters();

  // list clusters periodically:
  setInterval(clusters, refreshClusterList);

  // incrementally update cluster headers:
  //setInterval(updateClusters, refreshClusterDetails);

  // manually list clusters when user clicks the refresh button:
  $('#clusters > h2').click(function (event) {
    clusters();
  });

  // show cluster details when user clicks 'Details'
  // note: since it's an dynamically added element, needs the .on() form:
  $('body').on('click', 'span.detailsbtn', function () {
    var cID = $(this).parent().attr('id');
    clusterdetail(cID);
  });

  // when user clicks the create button in the right upper corner:
  $('#create').click(function (event) {
    $('#createdialog').show();
  });
  // when user clicks the Go! button in the dialog command row:
  $('#submitcc').click(function (event) {
    $('#createdialog').hide();
    createCluster();
  });
  // when user clicks the Cancel button in the dialog command row:
  $('#cancelcc').click(function (event) {
    $('#createdialog').hide();
  });

  // delete cluster lifetime for 30min when user clicks 'Delete'
  // note: since it's an dynamically added element, needs the .on() form:
  $('body').on('click', 'span.deletebtn', function () {
    var cID = $(this).parent().attr('id');
    deletecluster(cID);
  });

  $('body').on('click', 'span.showconfbtn', function () {
    var cID = $(this).parent().attr('id');
    clusterconf(cID);
  });
});

function createCluster() {
    console.info('Calling out to local proxy for cluster creation');
    $('#status').html('<img src="./standby.gif" alt="please wait" width="64px">');

    var cname = $('#icname').val();
    var cworkernum = $('#icworkernum').val();
    var ciamrole = $('#iciamrole').val();
    var cversion = $('#ickversion option:selected').text();
    var chelm = $('#ichelm option:selected').text();
    var toggrafana = $('#toggrafana').is(':checked');
    var togprom = $('#togprom').is(':checked');
    var togxray = $('#togxray').is(':checked');
    var togalb = $('#togalb').is(':checked');
    var togca = $('#togca').is(':checked');
    var toghpa = $('#toghpa').is(':checked');
    var toghelm=$('#toghelm').is(':checked');
    var togappmesh = $('#togappmesh').is(':checked');
    var clusterspec = { 
      'name': cname,
      'numworkers': parseInt(cworkernum, 10),
      'minworkers': parseInt(cworkermin, 10),
      'maxworkers': parseInt(cworkermax, 10),
      'iamrole': ciamrole,
      'kubeversion': cversion, 
      'addons':{
        'toghelm': toghelm,
        'togappmesh': togappmesh,
        'togprom': togprom,
        'toggrafana': toggrafana,
        'togxray': togxray,
        'togalb': togalb,
        'togca': togca,
        'toghpa': toghpa
      }
    };
    $.ajax({
      type: 'POST',
      url: cpURL+'/create',
      data: JSON.stringify(clusterspec),
      async: true,
      error: function (d) {
        console.info(d);
        $('#status').html('<div>'+ d.responseText + JSON.stringify(clusterspec) + '</div>');
      },
      success: function (d) {
        if (d != null) {
          console.info(d);
          $('#status').html('<div>Provisioning cluster with ID '+ d + JSON.stringify(clusterspec) + '</div>');
        }
      }
    });
}

function clusters(){
  $.ajax({
    type: 'POST',
    url: cpURL + '/list',
    dataType: 'json',
    async: true,
    error: function (d) {
      console.info(d.responseText);
      $('#status').html('<div>'+ d.responseText + '</div>');
    },
    success: function (d) {
      if (d != null) {
        console.info(d);
        var consoleLink = 'https://console.aws.amazon.com/eks/home?#/clusters/';
        var buffer = '';
        for (let i = 0; i < d.length; i++) {
          var cID = d[i];
          buffer += '<div class="cluster" id="' + cID + '">';
          buffer += ' <span class="cdlabel"><a href="" target="_blank" rel="noopener">' + cID + '</a></span>';
          buffer += '<span class="detailsbtn">Details</span> <span class="showconfbtn">Show Config</span> <span class="deletebtn">Delete</span>';
          buffer += '<div class="cdetails"></div>';
          buffer += '</div>';
        }
        $('#clusterdetails').html(buffer);
        $('#status').html('');
      }
    }
  })
}

function clusterdetail(cID) {
  var ep = '/status?cluster='+cID;
  $('#status').html('<img src="./standby.gif" alt="please wait" width="64px">');
  $.ajax({
    type: 'GET',
    url: cpURL + ep,
    dataType: 'json',
    async: true,
    error: function (d) {
      console.info(d);
      $('#status').html('<div>looking up details for cluster ' + cID + ' failed</div>');
    },
    success: function (d) {
      if (d != null) {
        console.info(d);
        var consoleLink = 'https://console.aws.amazon.com/eks/home?#/clusters/';
        var buffer = '';
        buffer += '<div class="cdfield"><span class="cdtitle">Name:</span> ' + d.name + '</div>';
        buffer += '<div class="cdfield"><span class="cdtitle">Kubernetes version:</span> ' + d.kubeversion + '</div>';
        var dbuffer = '';
        dbuffer += '<div class="moarfield"><span class="cdtitle">Status:</span> ' + d.status + '</div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">Endpoint:</span> <code class="inlinecode">' + d.endpoint + '</code></div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">Platform version:</span> ' + d.platformv + '</div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">IAM role:</span> <code class="inlinecode">' + d.iamrole + '</code></div>';
        buffer += '<div class="cdfield"><span class="cdtitle">Cluster summary:</span> ' + dbuffer + '</div>';
        $('#' + cID + ' .cdetails').html(buffer);
        $('#' + cID + ' .cdlabel a').attr('href', consoleLink + d.name);
        $('#' + cID + ' .cdlabel a').attr('title', 'this link takes you to the AWS console where you can view the details of the EKS cluster');
        $('#status').html('');
      }
    }
  })
}

function clusterconf(cID) {
  var ep = '/configof?cluster='+cID;
  $('#status').html('<img src="./standby.gif" alt="please wait" width="64px">');
  $.ajax({
    type: 'POST',
    url: cpURL + ep,
    dataType: 'json',
    async: true,
    error: function (d) {
      console.info(d);
      $('#status').html('<div>' + d.responseText  + '</div>');
    },
    success: function (d) {
      if (d != null) {
        console.info(d);
        var buffer = '';
        buffer += '<div class="configinstructions">';
        buffer += '<div class="cdfield"><span class="cdtitle">KubeConfig CLI for Cluster:</span> ' + d.name + '</div>';
        dbuffer += '<div class="cdfield"><span class="cdtitle">$</span> <code class="inlinecode">' + d.clicommand + '</code></div>';
        var dbuffer = '';
        dbuffer += '<div class="moarfield"><span class="cdtitle">$</span> <code class="inlinecode">' + d.clicommand + '</code></div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">Config Bucket:</span> ' + d.s3bucket + '</div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">IAM role:</span> <code class="inlinecode">' + d.iamrole + '</code></div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">Number of Workers:</span> ' + d.numworkers + '</div>';
        dbuffer += '<div class="moarfield"><span class="cdtitle">Addons Helm:</span> <code class="inlinecode">' + d.addons['toghelm'] + '</code></div>';
        buffer += '<div class="cdfield"><span class="cdtitle">Config summary:</span> ' + dbuffer + '</div>';
        $('#' + cID + ' .cdetails').html(buffer);
        $('#status').html('');
      }
    }
  })
}

function deletecluster(cID) {
  var ep = '/delete?cluster='+cID;
  console.info('Deleting EKS Cluster defined here');
  $('#status').html('<img src="./standby.gif" alt="please wait" width="64px">');
  $.ajax({
    type: 'POST',
    url: cpURL + ep,
    dataType: 'json',
    async: true,
    error: function (d) {
      console.info(d);
      $('#status').html('<div>'+ d + '</div>');
    },
    success: function (d) {
      if (d != null) {
        console.info(d);
        $('#status').html('<div>'+ d + '</div>');
        $('#clusterdetails').html('');
        clusters();
      }
    }
  });
}

// function vpc(cID) {
//   var ep = '/vpc';
//   $('#status').html('<img src="./standby.gif" alt="please wait" width="64px">');
//   $.ajax({
//     type: 'GET',
//     url: cpURL + ep,
//     dataType: 'json',
//     async: true,
//     error: function (d) {
//       console.info(d);
//       $('#status').html('<div>looking up details for vpcs in region ' + cID + ' failed</div>');
//     },
//     success: function (d) {
//       if (d != null) {
//         console.info(d);
        
//         return vpc;
//       }
//     }
//   })
// }