document.addEventListener('DOMContentLoaded', () => {
    // Add teacher
    document.getElementById('add-teacher-btn').addEventListener('click', () => {
        const select = document.getElementById('new-teacher');
        const teacherId = select.value;
        const teacherName = select.options[select.selectedIndex].text;

        if (teacherId) {
            const teacherList = document.getElementById('assigned-teachers');
            const teacherItem = document.createElement('div');
            teacherItem.classList.add('teacher-item');
            teacherItem.setAttribute('data-teacher-id', teacherId);

            teacherItem.innerHTML = `
                <span>${teacherName}</span>
                <button type="button" class="remove-teacher-btn" data-teacher-id="${teacherId}">Remove</button>
            `;
            teacherList.appendChild(teacherItem);

            // Reset the select box
            select.value = '';
        }
    });

    // Remove teacher
    document.getElementById('assigned-teachers').addEventListener('click', (event) => {
        if (event.target.classList.contains('remove-teacher-btn')) {
            const teacherId = event.target.getAttribute('data-teacher-id');
            const teacherItem = document.querySelector(`.teacher-item[data-teacher-id="${teacherId}"]`);
            teacherItem.remove();
        }
    });
});
