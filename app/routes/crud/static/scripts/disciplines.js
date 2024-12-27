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
    const disciplineInfoDiv = document.getElementById('discipline-info');

    disciplineDropdown.addEventListener('change', function() {
        const selectedDiscipline = disciplineDropdown.value;

        // Make AJAX request to get discipline info
        fetch(`/crud/get_discipline_info/${selectedDiscipline}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Populate the discipline info section
                disciplineInfoDiv.innerHTML = `
                    <p><strong>Código:</strong> ${data.code}</p>
                    <p><strong>Nome:</strong> ${data.name}</p>
                    <p><strong>Descrição:</strong> ${data.description}</p>
                    <p><strong>Créditos:</strong> ${data.credits}</p>
                `;

                // Make the section visible
                disciplineInfoSection.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching discipline info:', error);
            });
    });
});