/* =========================================================
   AI DATA ANALYST
   FRONTEND JAVASCRIPT
   ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("AI Data Analyst frontend loaded.");

    /*
     * Small visual enhancement:
     * Add a smooth fade-in to the main application.
     */
    const app = document.querySelector(".stApp");

    if (app) {
        app.style.opacity = "0";

        setTimeout(function () {
            app.style.transition = "opacity 0.35s ease";
            app.style.opacity = "1";
        }, 50);
    }

});