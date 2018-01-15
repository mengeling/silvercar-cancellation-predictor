$( "select.select" ).change(function () {
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/get_df_subset/",
    contentType: "application/json; charset=utf-8",
    data: { location: $( "#select-location option:selected" ).val(),
            month: $( "#select-month option:selected" ).val() },
    success: function(data) {
      $('.header').text(data.location + " Reservations");
      $('.total-count').text("Current Reservations: " + data.total_count);
      $('.cancel_count').text("Predicted Cancellations: " + data.cancel_count);
      $('.revenue').text("Predicted Revenue: " + data.revenue);
      $('.data').html(data.data);
    }
  });
})
.change();


$( ".form-input" ).change(function () {
  var data =
  console.log( data );
  $.ajax({
    type: "GET",
    url: $SCRIPT_ROOT + "/calculate_probability/",
    contentType: "application/json; charset=utf-8",
    data: { created_as_guest: $( "input[name='guest']:checked" ).val(),
            local_rental: $( "input[name='local']:checked" ).val(),
            awards_referral_bonus: $( "input[name='referral-bonus']:checked" ).val(),
            is_gds_user: $( "input[name='gds']:checked" ).val(),
            insurance: $( "input[name='insurance']:checked" ).val(),
            created_at: $( "input[name='created']" ).val(),
            pickup: $( "input[name='pickup']" ).val(),
            dropoff: $( "input[name='dropoff']" ).val(),
            used_promo: $( "input[name='promo']:checked" ).val(),
            used_referral: $( "input[name='referred']:checked" ).val(),
            credit_card: $( "input[name='credit-card']:checked" ).val(),
            web_booking: $( "input[name='web']:checked" ).val(),
            new_customer: $( "input[name='new-customer']:checked" ).val(),
            location: $( "select option:selected" ).val(),
            past_rides: $( "input[name='ride-count']" ).val(),
            past_cancellations: $( "input[name='cancel-count']" ).val() },
    success: function(data) {
      $('.probability').text("Probability: " + data.probability);
      $('.prediction').text("Prediction: " + data.prediction);
    }
  });
})
.change();