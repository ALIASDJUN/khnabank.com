// Fonction pour initialiser la page au chargement
document.addEventListener('DOMContentLoaded', function() {
    // Charger les données du localStorage ou utiliser les données par défaut
    loadAccountData();
    
    // Mettre à jour les données sur la page d'accueil
    updateHomePageData();

    // Ajouter les écouteurs d'événements
    setupEventListeners();
});

// Données du compte par défaut (si aucune donnée n'est trouvée dans localStorage)
const defaultAccountData = {
    accountNumber: "MN50 0005 00 5018191771",
    balance: 60000000000.96, // Solde initial
    transactions: [
        {
            date: "2025.04.27",
            time: "17:20",
            description: "Ухаалаг мэдээ үйлчилгээний хураамж",
            amount: -50.00,
            type: "up",
            remainingBalance: 29125.96
        },
        {
            date: "2025.04.27",
            time: "17:20",
            description: "QPay Payment",
            amount: -7800.00,
            type: "qr",
            remainingBalance: 36925.96
        }
    ]
};

// Variable pour stocker les données du compte
let accountData;

// Fonction pour charger les données du compte depuis localStorage
function loadAccountData() {
    const savedData = localStorage.getItem('bankAccountData');
    if (savedData) {
        accountData = JSON.parse(savedData);
    } else {
        accountData = {...defaultAccountData};
        saveAccountData();
    }
}

// Fonction pour sauvegarder les données du compte dans localStorage
function saveAccountData() {
    localStorage.setItem('bankAccountData', JSON.stringify(accountData));
}

// Fonction pour formater les montants avec séparateur de milliers
function formatAmount(amount) {
    return amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
}

// Fonction pour formater la date au format YYYY.MM.DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}.${month}.${day}`;
}

// Fonction pour formater l'heure au format HH:MM
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

// Fonction pour afficher la page sélectionnée et masquer les autres
function showPage(pageId) {
    // Masquer toutes les pages
    document.querySelectorAll('.page').forEach(page => {
        page.style.display = 'none';
    });

    // Afficher la page sélectionnée
    document.getElementById(pageId).style.display = 'block';

    // Mettre à jour les éléments actifs dans la navigation
    if (pageId === 'homePage') {
        updateActiveNavItem('home');
        updateHomePageData();
    } else if (pageId === 'qpayPage') {
        updateActiveNavItem('qpay');
    } else if (pageId === 'transactionPage') {
        updateActiveNavItem('transfer');
        resetTransferForm();
    }
}

// Fonction pour mettre à jour l'élément actif dans la navigation
function updateActiveNavItem(activeItem) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    if (activeItem === 'home') {
        document.querySelector('.nav-item:nth-child(1)').classList.add('active');
    } else if (activeItem === 'qpay') {
        document.querySelector('.nav-item:nth-child(2)').classList.add('active');
    } else if (activeItem === 'transfer') {
        document.querySelector('.nav-item:nth-child(3)').classList.add('active');
    }
}

// Fonction pour mettre à jour les données sur la page d'accueil
function updateHomePageData() {
    document.querySelector('.balance').textContent = formatAmount(accountData.balance);
    updateTransactionsList();
}

// Fonction pour mettre à jour la liste des transactions
function updateTransactionsList() {
    const transactionList = document.querySelector('.transaction-list');
    transactionList.innerHTML = '';

    const transactionsByDate = {};
    accountData.transactions.forEach(transaction => {
        if (!transactionsByDate[transaction.date]) {
            transactionsByDate[transaction.date] = [];
        }
        transactionsByDate[transaction.date].push(transaction);
    });

    const sortedDates = Object.keys(transactionsByDate).sort().reverse();

    sortedDates.forEach(date => {
        const dateDiv = document.createElement('div');
        dateDiv.className = 'transaction-date';
        dateDiv.textContent = date;
        transactionList.appendChild(dateDiv);

        transactionsByDate[date].forEach(transaction => {
            const transactionItem = createTransactionElement(transaction);
            transactionList.appendChild(transactionItem);
        });
    });
}

// Fonction pour créer un élément de transaction
function createTransactionElement(transaction) {
    const transactionItem = document.createElement('div');
    transactionItem.className = 'transaction-item';

    transactionItem.innerHTML = `
        <div class="transaction-time">${transaction.time}</div>
        <div class="transaction-details">
            <div class="transaction-icon ${transaction.type}">
                <i class="fas fa-${transaction.type === 'qr' ? 'qrcode' : 'arrow-up'}"></i>
            </div>
            <div class="transaction-info">
                <p class="transaction-description">${transaction.description}</p>
                <p class="transaction-remaining">Rem: ${formatAmount(transaction.remainingBalance)}</p>
            </div>
        </div>
        <div class="transaction-amount ${transaction.amount < 0 ? 'negative' : ''}">${transaction.amount < 0 ? '' : '+'}${formatAmount(transaction.amount)}</div>
    `;

    return transactionItem;
}

// Fonction pour configurer les écouteurs d'événements
function setupEventListeners() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function() {
            const navText = this.querySelector('p').textContent;
            let pageId;

            if (navText === 'Home') {
                pageId = 'homePage';
            } else if (navText === 'QPay') {
                pageId = 'qpayPage';
            } else if (navText === 'Transfer') {
                pageId = 'transactionPage';
            }

            showPage(pageId);
        });
    });

    const continueButton = document.querySelector('.continue-button');
    if (continueButton) {
        continueButton.addEventListener('click', processTransfer);
    }

    document.querySelectorAll('.back-button').forEach(button => {
        button.addEventListener('click', function() {
            showPage('homePage');
        });
    });

    const finishButton = document.querySelector('.primary-button');
    if (finishButton) {
        finishButton.addEventListener('click', function() {
            showPage('homePage');
        });
    }

    const amountDiv = document.querySelector('.amount');
    if (amountDiv) {
        amountDiv.addEventListener('click', function() {
            showNumericKeypad(this);
        });
    }

    // Écouteur pour la fonctionnalité QPay
    const qpayPage = document.getElementById('qpayPage');
    if (qpayPage) {
        const qrCode = qpayPage.querySelector('.qr-code');
        if (qrCode) {
            qrCode.addEventListener('click', processQPayPayment);
        }
    }
}

// Fonction pour réinitialiser le formulaire de transfert
function resetTransferForm() {
    const amountDiv = document.querySelector('.amount');
    if (amountDiv) {
        amountDiv.textContent = '0.00';
    }

    const inputFields = document.querySelectorAll('.input-field input');
    inputFields.forEach(input => {
        input.value = '';
    });
}

// Fonction pour traiter le transfert
function processTransfer() {
    const amountText = document.querySelector('.amount').textContent;
    const amount = parseFloat(amountText.replace(/,/g, '')) * -1;

    const recipientAccount = document.querySelector('.input-field input[placeholder="Enter account number"]').value;
    const recipientName = document.querySelector('.input-field input[placeholder="Enter recipient name"]').value;
    const description = document.querySelector('.input-field input[placeholder="Enter transaction description"]').value || "Transfer";

    if (!recipientAccount || !recipientName || amount === 0 || isNaN(amount)) {
        alert("Veuillez remplir tous les champs requis et entrer un montant valide.");
        return;
    }

    if (accountData.balance < Math.abs(amount)) {
        alert("Solde insuffisant pour effectuer cette transaction.");
        return;
    }

    const newBalance = accountData.balance + amount;

    const now = new Date();
    const newTransaction = {
        date: formatDate(now),
        time: formatTime(now),
        description: description,
        amount: amount,
        type: "up",
        remainingBalance: newBalance
    };

    accountData.transactions.unshift(newTransaction);
    accountData.balance = newBalance;
    
    // Sauvegarder les données dans localStorage
    saveAccountData();

    updateConfirmationPage(amount, recipientName, recipientAccount, description);
    showPage('confirmationPage');
}

// Fonction pour mettre à jour la page de confirmation
function updateConfirmationPage(amount, recipientName, recipientAccount, description) {
    const now = new Date();
    const formattedDate = `${now.getFullYear()}/${String(now.getMonth() + 1).padStart(2, '0')}/${String(now.getDate()).padStart(2, '0')}`;
    const formattedTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;

    document.querySelector('.success-amount').textContent = `${formatAmount(Math.abs(amount))} MNT`;
    document.querySelector('.transaction-date-time').textContent = `${formattedDate} ${formattedTime}`;

    const detailRows = document.querySelectorAll('.detail-row');
    detailRows[0].querySelector('.detail-value').innerHTML = `${formatAmount(accountData.balance)} ₮ <i class="fas fa-eye"></i>`;

    const truncatedName = recipientName.length > 10 ? recipientName.substring(0, 10) + '...' : recipientName;
    detailRows[1].querySelector('.detail-value').innerHTML = `${truncatedName} <span class="currency-badge small">₮</span>`;

    detailRows[2].querySelector('.detail-label').textContent = recipientAccount;

    detailRows[3].querySelector('.detail-value').textContent = description;
}

// Simulation d'un clavier numérique pour entrer le montant
function showNumericKeypad(amountElement) {
    const amount = prompt("Entrez le montant:", amountElement.textContent);
    if (amount !== null && !isNaN(parseFloat(amount))) {
        amountElement.textContent = formatAmount(parseFloat(amount));
    }
}

// Fonction pour simuler un paiement QPay
function processQPayPayment() {
    const amount = prompt("Entrez le montant du paiement QPay:", "0.00");

    if (amount === null || isNaN(parseFloat(amount))) {
        return;
    }

    const paymentAmount = parseFloat(amount) * -1;

    if (accountData.balance < Math.abs(paymentAmount)) {
        alert("Solde insuffisant pour effectuer ce paiement.");
        return;
    }

    const newBalance = accountData.balance + paymentAmount;

    const now = new Date();
    const newTransaction = {
        date: formatDate(now),
        time: formatTime(now),
        description: "QPay Payment",
        amount: paymentAmount,
        type: "qr",
        remainingBalance: newBalance
    };

    accountData.transactions.unshift(newTransaction);
    accountData.balance = newBalance;
    
    // Sauvegarder les données dans localStorage
    saveAccountData();

    alert("Paiement QPay effectué avec succès!");
    showPage('homePage');
}

// Fonction pour réinitialiser les données (utile pour le débogage)
function resetData() {
    if (confirm("Êtes-vous sûr de vouloir réinitialiser toutes les données?")) {
        localStorage.removeItem('bankAccountData');
        loadAccountData();
        updateHomePageData();
        alert("Données réinitialisées avec succès!");
    }
}