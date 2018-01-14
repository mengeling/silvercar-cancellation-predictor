$(document).ready(function() {
  $( "select" ).change(function () {
    $.ajax({
      type: "GET",
      url: $SCRIPT_ROOT + "/location_subset/",
      contentType: "application/json; charset=utf-8",
      data: { location: $( "select option:selected" ).val() },
      success: function(data) {
        $('.header').text(data.location + " Reservations");
        $('.total-count').text("Current Reservations: " + data.total_count);
        $('.cancel_count').text("Predicted Cancellations: " + data.cancel_count);
        $('.data').html(data.data);
      }
    });
  }).change();
});