document.addEventListener('DOMContentLoaded', function() {
    const categoryDropdown = document.getElementById('discipline-category');
    const disciplineDropdown = document.getElementById('discipline-list');

    categoryDropdown.addEventListener('change', function() {
        const selectedCategory = categoryDropdown.value;

        // Make AJAX request to get disciplines
        fetch(`/crud/get_disciplines/${selectedCategory}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear existing options
                disciplineDropdown.innerHTML = '';

                // Populate new options
                data.forEach(discipline => {
                    const option = document.createElement('option');
                    option.value = discipline.id;
                    option.textContent = discipline.code + " - " + discipline.name;
                    disciplineDropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching disciplines:', error);
            });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const disciplineDropdown = document.getElementById('discipline-list');
    const disciplineInfoSection = document.getElementById('discipline-info-section');
    const disciplineSummarySection = document.getElementById('discipline-summary-section');
    const modulesTableBody = document.querySelector('#modules-table tbody');
    const disciplineTableBody = document.querySelector('#discipline-summary-table tbody');
    const applyChangesButton = document.getElementById('apply-changes');
    
    // const discCodeSpan = document.getElementById('disc-code');
    // const discNameInput = document.getElementById('disc-name');
    // const discAbbreviationInput = document.getElementById('disc-abbreviation');
   
    disciplineDropdown.addEventListener('change', function() {
        const selectedDiscipline = disciplineDropdown.value;

        // Make AJAX request to get modules
        fetch(`/crud/get_discipline_info/${selectedDiscipline}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Clear existing table rows
                disciplineTableBody.innerHTML = '';
                modulesTableBody.innerHTML = '';

                // Populate discipline summary
                const summaryRow = document.createElement('tr');


                const tCode = data.modules[0].disc_code;
                const name = data.modules[0].name;
                const AbbrName = data.modules[0].abbrName;
                const workLoad = data.discipline.workload;
                const selectedRoom = data.discipline.mandatory_room;

                summaryRow.innerHTML = `
                    <td>${tCode}</td>
                    <td><input type="text" value="${name}" class="name"></td>
                    <td><input type="text" value="${AbbrName}" class="abbrName"></td>
                    <td><input type="number" value="${workLoad}" class="workload" style="width: 50px;"></td>
                    <td>${createRoomDropdown(selectedRoom, data.classrooms)}</td>
                    <td></td>
                    <td></td>
                    <td><button onclick="forbidden()" class="remove-module">Remover</button></td>
                `;

                disciplineTableBody.appendChild(summaryRow);

                disciplineSummarySection.style.display = 'block';

                // Populate modules grid
                data.modules.forEach((module, index) => {
                    teacher1 = module.teachers[0]?.teacher_name || '-';
                    teacher2 = module.teachers[1]?.teacher_name || '-';
                    teacher3 = module.teachers[2]?.teacher_name || '-';
    
                    const row = document.createElement('tr');

                    row.innerHTML = `
                        <td>${module.code}</td>
                        <td>${createTeacherDropdown(teacher1, data.teachersNames, index, 1)}</td>
                        <td>${createTeacherDropdown(teacher2, data.teachersNames, index, 2)}</td>
                        <td>${createTeacherDropdown(teacher3, data.teachersNames, index, 3)}</td>
                        <td><button onclick="forbidden()" class="remove-module" data-index="${index}">Remover</button></td>
                    `;
                    modulesTableBody.appendChild(row);
                });

                // Show apply changes button
                applyChangesButton.style.display = 'block';

                // Make the section visible
                disciplineInfoSection.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching discipline info:', error);
            });
    });

    // Handle apply changes button click
applyChangesButton.addEventListener('click', function() {
    const updatedInfo = {
        disciplineSummary: {},
        modules: []
    };

    // Collect discipline summary information
    const summaryRow = disciplineTableBody.querySelector('tr');
    if (summaryRow) {
        const summaryInputs = summaryRow.querySelectorAll('input');
        updatedInfo.disciplineSummary = {
            code: summaryRow.children[0].textContent.trim(),
            name: summaryInputs[0]?.value.trim() || '',
            abbreviation: summaryInputs[1]?.value.trim() || '',
            workLoad: summaryInputs[2]?.value.trim() || '',
        };
    }

    // Collect modules information
    const moduleRows = modulesTableBody.querySelectorAll('tr');
    moduleRows.forEach(row => {
        const moduleData = {
            code: row.children[0].textContent.trim(),
            teachers: []
        };

        // Collect teacher selections
        const teacherDropdowns = row.querySelectorAll('.teacher-dropdown');
        teacherDropdowns.forEach(dropdown => {
            moduleData.teachers.push(dropdown.value.trim());
        });

        updatedInfo.modules.push(moduleData);
    });

    // Send updated info to the server
    fetch('/crud/update_discipline', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedInfo),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update information');
            }
            alert('Alterações aplicadas com sucesso!');
        })
        .catch(error => {
            console.error('Error applying changes:', error);
        });
    });

    function createRoomDropdown(selectedRoomName, roomTuples) {
        const dropdown = document.createElement('select');
        dropdown.classList.add('room-dropdown');
        
        dropdown.setAttribute('disabled', 'disabled');

        roomTuples.forEach(roomTuple => {
            const roomID = roomTuple[0];
            const roomName = roomTuple[1];

            const option = document.createElement('option');
            option.value = roomID;
            option.textContent = roomName;
            if (roomName === selectedRoomName) {
                option.setAttribute('selected', 'selected');
            }
            dropdown.appendChild(option);
        });

        return dropdown.outerHTML;
    }

    function createTeacherDropdown(selectedTeacherName, teachersTuples, moduleIndex, teacherIndex) {
        const dropdown = document.createElement('select');
        dropdown.classList.add('teacher-dropdown');
        dropdown.dataset.index = moduleIndex;
        dropdown.dataset.teacher = teacherIndex;

        teachersTuples.forEach(teacherTuple => {
            const teacherId = teacherTuple[0];
            const teacherName = teacherTuple[1];

            const option = document.createElement('option');
            option.value = teacherId;
            option.textContent = teacherName;
            if (teacherName === selectedTeacherName) {
                option.setAttribute('selected', 'selected');
            }
            dropdown.appendChild(option);
        });

        return dropdown.outerHTML;
    }
});


function delModule(button, code) {
    fetch('/crud/delete-module', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete module');
            }
            alert('Módulo apagado com sucesso!');
            const row = button.closest('tr'); // Ensure correct DOM traversal
            if (row) {
                row.remove(); // Remove the entire row
            } else {
                console.error('Row not found for the button.');
            }
        })
        .catch(error => {
            console.error('Error deleting module:', error);
        });
}


function forbidden() {
    alert('Você não tem permissão para executar esta operação!');
}