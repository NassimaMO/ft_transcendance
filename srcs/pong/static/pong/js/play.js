document.addEventListener("DOMContentLoaded", function () {
    const modeField = document.getElementById("id_mode");
    const connectField = document.getElementById("connect-group");
    const matchmakingField = document.getElementById("id_mm");
    const tournamentOption = matchmakingField.querySelector("option[value='tournoi']");

    function updateFields() {
        const mode = modeField.value;

        if (mode === "multi") {
            connectField.style.display = "block";
            if (!matchmakingField.contains(tournamentOption)) {
                matchmakingField.appendChild(tournamentOption);
            }
        } else {
            connectField.style.display = "none";
            if (matchmakingField.contains(tournamentOption)) {
                tournamentOption.remove();
            }
        }
    }

    modeField.addEventListener("change", updateFields);
    updateFields();
});
