const form = document.getElementById("forecastForm");
const storeInput = document.getElementById("store");
const itemInput = document.getElementById("item");
const dateInput = document.getElementById("date");
const resetBtn = document.getElementById("resetBtn");
const submitBtn = document.getElementById("submitBtn");
const clientError = document.getElementById("clientError");

if (form) {
    form.addEventListener("submit", function (event) {
        clientError.classList.add("hidden");
        clientError.textContent = "";

        const store = parseInt(storeInput.value, 10);
        const item = parseInt(itemInput.value, 10);
        const date = dateInput.value;

        if (!store || store < 1) {
            event.preventDefault();
            showError("Please enter a valid Store ID greater than 0.");
            return;
        }

        if (!item || item < 1) {
            event.preventDefault();
            showError("Please enter a valid Item ID greater than 0.");
            return;
        }

        if (!date) {
            event.preventDefault();
            showError("Please select a valid date.");
            return;
        }

        submitBtn.classList.add("loading");
        submitBtn.textContent = "Generating...";
    });
}

if (resetBtn) {
    resetBtn.addEventListener("click", function () {
        storeInput.value = "";
        itemInput.value = "";
        dateInput.value = "";
        clientError.classList.add("hidden");
        clientError.textContent = "";
    });
}

function showError(message) {
    clientError.textContent = message;
    clientError.classList.remove("hidden");
}