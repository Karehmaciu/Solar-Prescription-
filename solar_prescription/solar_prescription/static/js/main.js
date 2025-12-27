// Solar Prescription - Frontend JavaScript

// Location autocomplete
document.addEventListener("DOMContentLoaded", function () {
  const locationInput = document.getElementById("locationSearch");
  const suggestionsDiv = document.getElementById("locationSuggestions");
  const coordsDisplay = document.getElementById("coordinatesDisplay");
  const latInput = document.getElementById("latitude");
  const lonInput = document.getElementById("longitude");
  const locationNameInput = document.getElementById("locationName");

  // Enable quantity inputs when appliance is selected
  const applianceCheckboxes = document.querySelectorAll(
    'input[name="appliance"]'
  );
  applianceCheckboxes.forEach((checkbox) => {
    const qtyInputId = checkbox.dataset.qtyInput;
    const qtyInput = document.getElementById(qtyInputId);

    // Initial state
    if (qtyInput) {
      qtyInput.disabled = !checkbox.checked;
    }

    checkbox.addEventListener("change", function () {
      const qtyInputId = this.dataset.qtyInput;
      const qtyInput = document.getElementById(qtyInputId);
      if (!qtyInput) return;

      qtyInput.disabled = !this.checked;
      if (this.checked) {
        if (!qtyInput.value || parseInt(qtyInput.value) < 1) {
          qtyInput.value = "1";
        }
        qtyInput.focus();
      }
    });
  });

  // Location search
  if (locationInput) {
    locationInput.addEventListener("input", function () {
      const query = this.value.trim();

      if (query.length < 2) {
        suggestionsDiv.innerHTML = "";
        return;
      }

      // Call the geocoding API
      fetch(`/api/geocode?q=${encodeURIComponent(query)}`)
        .then((response) => response.json())
        .then((data) => {
          const matches = Object.entries(data).slice(0, 5);

          if (matches.length > 0) {
            suggestionsDiv.innerHTML = matches
              .map(
                ([name, coords]) =>
                  `<div class="location-suggestion" data-lat="${coords.lat}" data-lon="${coords.lon}" data-name="${name}">
                                ${name}
                            </div>`
              )
              .join("");

            // Add click handlers
            suggestionsDiv
              .querySelectorAll(".location-suggestion")
              .forEach((item) => {
                item.addEventListener("click", function () {
                  const lat = this.dataset.lat;
                  const lon = this.dataset.lon;
                  const name = this.dataset.name;

                  locationInput.value = name;
                  latInput.value = lat;
                  lonInput.value = lon;
                  locationNameInput.value = name;

                  coordsDisplay.style.display = "block";
                  document.getElementById(
                    "coordsText"
                  ).textContent = `${lat}, ${lon}`;

                  suggestionsDiv.innerHTML = "";
                });
              });
          } else {
            suggestionsDiv.innerHTML =
              '<div class="location-suggestion">No matching locations found. Try: Nairobi, Lagos, or Johannesburg</div>';
          }
        })
        .catch((error) => {
          console.error("Geocoding error:", error);
          suggestionsDiv.innerHTML =
            '<div class="location-suggestion">Error fetching locations. Try again.</div>';
        });
    });

    // Close suggestions when clicking outside
    document.addEventListener("click", function (e) {
      if (
        !locationInput.contains(e.target) &&
        !suggestionsDiv.contains(e.target)
      ) {
        suggestionsDiv.innerHTML = "";
      }
    });
  }

  // Form submission
  const form = document.getElementById("prescriptionForm");
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      // Validate location is selected
      if (!latInput.value || !lonInput.value) {
        alert("Please select a location from the suggestions");
        return;
      }

      // Get selected kit size
      const kitSize = document.querySelector('input[name="kitSize"]:checked');
      if (!kitSize) {
        alert("Please select a kit size");
        return;
      }

      // Get selected coverage percentage
      const coverage = document.querySelector('input[name="coverage"]:checked');
      if (!coverage) {
        alert("Please select a coverage percentage");
        return;
      }

      // Get selected appliances
      const appliances = [];
      applianceCheckboxes.forEach((checkbox) => {
        if (checkbox.checked) {
          const qtyInputId = checkbox.dataset.qtyInput;
          const quantity =
            parseInt(document.getElementById(qtyInputId).value) || 1;
          appliances.push({
            id: checkbox.value,
            quantity: quantity,
          });
        }
      });

      if (appliances.length === 0) {
        alert("Please select at least one appliance");
        return;
      }

      // Prepare data
      const formData = {
        location: locationNameInput.value,
        latitude: parseFloat(latInput.value),
        longitude: parseFloat(lonInput.value),
        kit_size: parseInt(kitSize.value),
        coverage_percentage: parseInt(coverage.value),
        appliances: appliances,
      };

      // Show loading
      document.getElementById("loadingSpinner").style.display = "block";
      document.getElementById("submitBtn").disabled = true;
      document.getElementById("errorMessage").style.display = "none";

      try {
        const response = await fetch("/prescribe", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (result.success) {
          // Redirect to results page
          window.location.href = "/results";
        } else {
          throw new Error(result.error || "An error occurred");
        }
      } catch (error) {
        document.getElementById("errorMessage").textContent = error.message;
        document.getElementById("errorMessage").style.display = "block";
        document.getElementById("submitBtn").disabled = false;
      } finally {
        document.getElementById("loadingSpinner").style.display = "none";
      }
    });
  }
});
