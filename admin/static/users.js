document.addEventListener("DOMContentLoaded", function () {
    const addUserForm = document.getElementById("addUserForm");
    const userTableBody = document.getElementById("userTable");
    const userNameInput = document.getElementById("userName");

    let users = [];
    let userId = 1; // Unique ID counter

    // Function to render users in the table
    function renderUsers() {
        userTableBody.innerHTML = ""; // Clear existing rows

        users.forEach((user, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>
                    <button onclick="removeUser(${user.id})">Remove</button>
                </td>
            `;
            userTableBody.appendChild(row);
        });
    }

    // Add user
    addUserForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const userName = userNameInput.value.trim();
        if (userName === "") return;

        users.push({ id: userId++, name: userName });
        renderUsers();

        userNameInput.value = ""; // Clear input field
    });

    // Remove user function
    window.removeUser = function (id) {
        users = users.filter(user => user.id !== id);
        renderUsers();
    };
});
