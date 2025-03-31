// Update grievance status
function updateStatus(id) {
    const newStatus = document.getElementById(`status-${id}`).value;
    if (!newStatus) {
        alert("Please enter a new status!");
        return;
    }

    // Find the corresponding row and update its status
    const rows = document.querySelectorAll("tbody tr");
    rows.forEach((row) => {
        if (row.children[0].textContent == id) {
            row.children[4].textContent = newStatus; // Update status column
        }
    });

    alert(`Grievance ID ${id} status updated successfully!`);
}
