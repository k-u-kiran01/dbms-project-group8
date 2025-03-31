const dealers = [
    { id: 1, name: "John Doe", contact: "9876543210", status: "Active" },
    { id: 2, name: "Jane Smith", contact: "8765432109", status: "Inactive" },
];

const dealerTable = document.getElementById("dealerTable");

dealers.forEach((dealer) => {
    const row = document.createElement("tr");
    row.innerHTML = `
        <td>${dealer.id}</td>
        <td>${dealer.name}</td>
        <td>${dealer.contact}</td>
        <td>${dealer.status}</td>`;
    dealerTable.appendChild(row);
});
