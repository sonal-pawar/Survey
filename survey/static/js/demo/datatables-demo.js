// Call the dataTables jQuery plugin
$(document).ready(function() {
  $('#dataTable').DataTable({
        "pageLength": 5,
        "bLengthChange": false,
        "searching": false,
        "ordering": true
    });
});
