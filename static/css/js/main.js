// Search Table
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId).value.toLowerCase();
    const table = document.getElementById(tableId);
    const tr = table.getElementsByTagName("tr");
    for (let i = 1; i < tr.length; i++) {
        let display = false;
        const tds = tr[i].getElementsByTagName("td");
        for (let j = 0; j < tds.length; j++) {
            if (tds[j].innerText.toLowerCase().includes(input)) {
                display = true;
                break;
            }
        }
        tr[i].style.display = display ? "" : "none";
    }
}

// Chatbot
function sendMessage(event, inputId, messagesDivId) {
    if (event.key === 'Enter') {
        const input = document.getElementById(inputId);
        const messagesDiv = document.getElementById(messagesDivId);
        const userMsg = input.value;
        if (!userMsg) return;
        messagesDiv.innerHTML += `<div><b>You:</b> ${userMsg}</div>`;
        
        // Simple chatbot response
        let botMsg = "I am here to assist you!";
        if (userMsg.toLowerCase().includes("fund")) botMsg = "The principal sets the total government fund.";
        if (userMsg.toLowerCase().includes("expenditure")) botMsg = "Financer can add expenditures in the categories.";

        messagesDiv.innerHTML += `<div><b>Bot:</b> ${botMsg}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        input.value = "";
    }
}

// Chart
function createChart(ctx, labels, data) {
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Spent Amount',
                data: data,
                backgroundColor: '#4b7bec'
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}
