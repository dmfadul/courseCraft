function changeWeek(direction) {
    const currentWeekNumber = parseInt(window.location.pathname.split('/').pop());
    const currentClass = window.location.pathname.split('/')[2];
    const currentPage = window.location.pathname.split('/')[1];
    const newWeekNumber = currentWeekNumber + direction;
    console.log(currentPage, currentClass, newWeekNumber)
    window.location.href = `/${currentPage}/${currentClass}/${newWeekNumber}`;
}

function changeCohort(cohortCode) {
    const currentPage = window.location.pathname.split('/')[1];
    const currentWeekNumber = parseInt(document.getElementById('weekSelect').value);
    window.location.href = `/${currentPage}/${cohortCode}/${currentWeekNumber}`;
}

function changeWeekDirect(weekNumber) {
    const currentPage = window.location.pathname.split('/')[1];
    const currentCohortCode = document.getElementById('cohortSelect').value;
    window.location.href = `/${currentPage}/${currentCohortCode}/${weekNumber}`;
}

// Function to extract classCode and week from the current URL
function getClassCodeAndWeekFromUrl() {
    const pathParts = window.location.pathname.split('/');
    const gridType = pathParts[1];
    const classCode = pathParts[2];
    const week = pathParts[3];
    return { gridType, classCode, week };
}

// Function to set the print button URL
function setPrintButtonUrl() {
    const { gridType, classCode, week } = getClassCodeAndWeekFromUrl();
    const printButton = document.getElementById('printButton');
    printButton.onclick = function() {
        window.location.href = `/print/${gridType}/${classCode}/${week}`;
    };
}

function setPrintAllButtonUrl() {
    const { gridType, classCode, week } = getClassCodeAndWeekFromUrl();
    const printButton = document.getElementById('printAllButton');
    printButton.onclick = function() {
        console.log(gridType, classCode)
        window.location.href = `/print_all/${gridType}/${classCode}`;
    };
}


// Set the print button URL when the page loads
window.onload = setPrintButtonUrl;
window.onload = setPrintAllButtonUrl;

document.addEventListener("keydown", function(event) {
    if (event.key === "ArrowLeft") {
        // Simulate click on the left-arrow-button
        const leftArrowButton = document.getElementById("left-arrow-button");
        if (leftArrowButton) {
            leftArrowButton.click();
        }
    } else if (event.key === "ArrowRight") {
        // Simulate click on the right-arrow-button
        const rightArrowButton = document.getElementById("right-arrow-button");
        if (rightArrowButton) {
            rightArrowButton.click();
        }
    }
});
