const warehouses = [
    { id: 1, location: "Delhi", capacity: 5000, availableStock: 3000 },
    { id: 2, location: "Mumbai", capacity: 7000, availableStock: 4500 },
    { id: 3, location: "Chennai", capacity: 6000, availableStock: 2000 },
];

const tableBody = document.getElementById("warehouseTable");

// Populate warehouses table
warehouses.forEach((warehouse) => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${warehouse.id}</td>
        <td>${warehouse.location}</td>
        <td>${warehouse.capacity}</td>
        <td>${warehouse.availableStock}</td>`;
    tableBody.appendChild(row);
});

// Search warehouse by ID
function searchWarehouse() {
    const searchId = document.getElementById("searchWarehouse").value;
    
    if (!searchId) {
        alert("Please enter a Warehouse ID to search!");
        return;
    }

    const filteredWarehouses = warehouses.filter((w) => w.id == searchId);

    // Clear existing rows in the table
    tableBody.innerHTML = "";

    filteredWarehouses.forEach((warehouse) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${warehouse.id}</td>
            <td>${warehouse.location}</td>
            <td>${warehouse.capacity}</td>
            <td>${warehouse.availableStock}</td>`;
        
        tableBody.appendChild(row);
    });

    if (filteredWarehouses.length === 0) {
        alert(`No warehouse found with ID ${searchId}`);
    }
}
