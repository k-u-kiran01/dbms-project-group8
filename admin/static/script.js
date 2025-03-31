// script.js

// Function to search grievances (placeholder functionality)
function searchGrievance() {
    const searchId = document.getElementById('search-id').value.trim();
    if (searchId) {
        alert(`Searching for Grievance ID: ${searchId}`);
        // Logic to filter grievances can be added here
    } else {
        alert('Please enter a valid Grievance ID.');
    }
}

// Function to update grievance status
function updateStatus(grievanceId) {
    const statusInput = document.getElementById(`status-${grievanceId}`).value.trim();
    
    if (statusInput) {
        alert(`Updating Grievance ID ${grievanceId} to status "${statusInput}"`);
        // Logic to update status can be added here
        document.getElementById(`status-${grievanceId}`).value = ''; // Clear input field
    } else {
        alert('Please enter a new status.');
    }
}
