const procurements = [
    { id: 1, item: "Wheat", quantity: "1000 kg", status: "Completed" },
    { id: 2, item: "Rice", quantity: "500 kg", status: "Pending" },
    { id: 3, item: "Sugar", quantity: "300 kg", status: "In Progress" },
];

const tableBody = document.getElementById("procurementTable");

procurements.forEach((procurement) => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${procurement.id}</td>
        <td>${procurement.item}</td>
        <td>${procurement.quantity}</td>
        <td>${procurement.Price}</td>
        <td>${procurement.status}</td>`;
    tableBody.appendChild(row);
});
