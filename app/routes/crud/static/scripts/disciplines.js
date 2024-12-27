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
                    option.textContent = discipline.name;
                    disciplineDropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching disciplines:', error);
            });
    });
});