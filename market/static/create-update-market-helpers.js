// Scripts used in create.html and edit-market.html

function submit_form() {
    // If user wants to create an "endless" game 
    if (document.getElementById('id_endless').checked) {
        // Set value of max_rounds to a valid number (some positive integer less than the chosen limit)
        // before submitting the form (the exact value will not matter in endless games): 
        document.getElementById('id_max_rounds').value = 15;
    }
    market_form.submit();
}

function adjust_max_round_field() {
    // This exact function is also defined in create.html
    upper_limit_on_max_rounds = parseInt("{{ upper_limit_on_max_rounds }}")
    max_rounds_field = document.getElementById('div_id_max_rounds')
    if (document.getElementById('id_endless').checked) {
        max_rounds_field.style.visibility = "hidden";
    } else {
        max_rounds_field.style.visibility = "";
    }
}