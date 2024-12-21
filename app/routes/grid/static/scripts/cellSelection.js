let selectedCells = [];
let ctrlKeyPressed = false;
let getAllDisciplines = false;

$(document).ready(function() {
    $('#data-table').on('click', 'td', function(e) {
        // Check if the Shift key is pressed, if not, do nothing
        if (!e.shiftKey) {
            return;
        }
        
        const cellIndex = selectedCells.indexOf(this);
        if (cellIndex > -1) {
            // Cell is already selected, remove it from the array
            selectedCells.splice(cellIndex, 1);
            $(this).removeClass('highlighted'); // Remove highlighting
        } else {
            // New cell selected, add to the array
            selectedCells.push(this);
            $(this).addClass('highlighted'); // Add highlighting
        }
    });

    $(document).on('keyup keydown', function(e) {
        if (e.type === 'keydown') {
            if (e.which === 17) {
                ctrlKeyPressed = true;
                getAllDisciplines = true;
            }
        } else if (e.type === 'keyup') {
            if (e.which === 17) {
                ctrlKeyPressed = false;
            }
            if (e.which === 16 && selectedCells.length > 0) {
                showCellModal();
            }
        }
    });
    
    $('#confirm-btn').click(function() {
        const selectedOption = $('#dropdown-select').val();
        const selectedClassroom = $('#dropdown-select-classrooms').val();
        const repeatWeekly = $('#weekly-repeat').is(':checked');  // Get the checkbox state
        const joinCohorts = $('#joined-cohorts').is(':checked');  // Get the checkbox state
        const forced = $('#force-creation').is(':checked');  // Get the checkbox state

        const dataToSend = selectedCells.map(cell => {
            return {
                rowId: $(cell).closest('tr').find('td:first').text(),
                columnIndex: $(cell).index(),
                selectedOption: selectedOption,
                selectedClassroom: selectedClassroom,
                startingWeek: startingWeek,
                classCode: classNumber,
                repeatWeekly: repeatWeekly,
                joinCohorts: joinCohorts,
                forced: forced,
                getAllDisciplines: getAllDisciplines,
            };
        });

        // AJAX call to send data back to Flask
        $.ajax({
            type: 'POST',
            url: '/update',  // Ensure this Flask route is defined
            data: JSON.stringify(dataToSend),
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                console.log('Data sent successfully');
                window.location.reload(); // Reload the page after sending data
            }
        });
        $('#cellModal').modal('hide'); // Hide modal after sending data
    });

    // Handling modal close event to clear selections
    $('#cellModal').on('hidden.bs.modal', function () {
        $('.highlighted').removeClass('highlighted');
        selectedCells = []; // Clear selected cells array
    });
});

function showCellModal() {
    if (selectedCells.length > 0) {
        let options;
        if (ctrlKeyPressed) {
            options = disciplineListAll; // Use the list with Ctrl pressed
        } else {
            options = disciplineList; // Use the default list
        }

        const select = $('#dropdown-select');
        select.empty();
        options.forEach(option => {
            select.append(new Option(option, option));
        });

        $('#cellModal').modal('show');
    }
}
