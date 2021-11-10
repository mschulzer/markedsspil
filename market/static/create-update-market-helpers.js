// Scripts used in create_market_details.html and edit-market.html

function adjust_max_round_field() {
    max_rounds_field = document.getElementById('div_id_max_rounds')
    if (document.getElementById('id_endless').checked) {
        max_rounds_field.style.visibility = "hidden";
    } else {
        max_rounds_field.style.visibility = "";
    }
}