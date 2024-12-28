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
    
    const discCodeSpan = document.getElementById('disc-code');
    const discNameInput = document.getElementById('disc-name');
    const discAbbreviationInput = document.getElementById('disc-abbreviation');
   
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


                const tCode = "codeTeste";
                const name = "teste";
                const AbbrName = "teste..";

                summaryRow.innerHTML = `
                    <td>${tCode}</td>
                    <td><input type="text" value="${name}" class="teacher" data-teacher="1"></td>
                    <td><input type="text" value="${AbbrName}" class="teacher" data-teacher="2"></td>
                    <td><button class="remove-module">Remover</button></td>
                `;

                disciplineTableBody.appendChild(summaryRow);

                disciplineSummarySection.style.display = 'block';

                // Populate modules grid
                data.forEach((module, index) => {
                    teacher1 = module.teachers[0] || '';
                    teacher2 = module.teachers[1] || '';
                    teacher3 = module.teachers[2] || '';
    
                    if (teacher1) {
                        teacher1 = teacher1.teacher_name;
                    }
                    if (teacher2) {
                        teacher2 = teacher2.teacher_name;
                    }
                    if (teacher3) {
                        teacher3 = teacher3.teacher_name;
                    }

                    const row = document.createElement('tr');

                    row.innerHTML = `
                        <td>${module.code}</td>
                        <td>${module.name}</td>
                        <td><input type="text" value="${teacher1}" data-index="${index}" class="teacher" data-teacher="1"></td>
                        <td><input type="text" value="${teacher2}" data-index="${index}" class="teacher" data-teacher="2"></td>
                        <td><input type="text" value="${teacher3}" data-index="${index}" class="teacher" data-teacher="3"></td>
                        <td><button class="remove-module" data-index="${index}">Remover</button></td>
                    `;
                    modulesTableBody.appendChild(row);
                });

                // Show apply changes button
                applyChangesButton.style.display = 'block';

                // Add remove button functionality
                document.querySelectorAll('.remove-module').forEach(button => {
                    button.addEventListener('click', function() {
                        const index = this.getAttribute('data-index');
                        data.modules.splice(index, 1);
                        this.parentElement.innerHTML = '';
                    });
                });

                // Make the section visible
                disciplineInfoSection.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching discipline info:', error);
            });
    });

    // Handle apply changes button click
    applyChangesButton.addEventListener('click', function() {
        const updatedModules = [];
        const rows = modulesGrid.querySelectorAll(':scope > input, :scope > button');

        for (let i = 0; i < rows.length; i += 6) {
            updatedModules.push({
                code: rows[i].value,
                name: rows[i + 1].value,
                teachers: [
                    rows[i + 2].value,
                    rows[i + 3].value,
                    rows[i + 4].value,
                ]
            });
        }

        // Send updated modules to the server
        fetch('/update_modules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ modules: updatedModules }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to update modules');
                }
                alert('Alterações aplicadas com sucesso!');
            })
            .catch(error => {
                console.error('Error applying changes:', error);
            });
    });
});