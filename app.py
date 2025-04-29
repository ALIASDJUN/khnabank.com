import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import re
import locale
from PIL import Image, ImageTk
from io import BytesIO
import qrcode

class BankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banque App")
        self.root.geometry("375x700")  # Taille standard pour smartphone
        self.root.resizable(False, False)
        
        # Données du compte (simulation de base de données)
        self.account_data = {
            "accountNumber": "MN50 0005 00 5018191771",
            "balance": 29125.96,  # Solde initial
            "transactions": [
                {
                    "date": "2025.04.27",
                    "time": "17:20",
                    "description": "Ухаалаг мэдээ үйлчилгээний хураамж",
                    "amount": -50.00,
                    "type": "up",
                    "remainingBalance": 29125.96
                },
                {
                    "date": "2025.04.27",
                    "time": "17:20",
                    "description": "QPay Payment",
                    "amount": -7800.00,
                    "type": "qr",
                    "remainingBalance": 36925.96
                }
            ]
        }
        
        # Créer le conteneur principal pour les pages
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Créer les différentes pages
        self.pages = {
            "homePage": self.create_home_page(),
            "qpayPage": self.create_qpay_page(),
            "transactionPage": self.create_transaction_page(),
            "confirmationPage": self.create_confirmation_page()
        }
        
        # Créer la barre de navigation en bas
        self.create_navigation_bar()
        
        # Afficher la page d'accueil au début
        self.show_page("homePage")
    
    def create_home_page(self):
        page = tk.Frame(self.container, bg="#f5f5f5")
        
        # En-tête avec solde
        header = tk.Frame(page, bg="#0080ff", height=150)
        header.pack(fill="x")
        
        balance_label = tk.Label(header, text="Balance", fg="white", bg="#0080ff", font=("Arial", 14))
        balance_label.place(x=20, y=30)
        
        self.balance_display = tk.Label(header, text=self.format_amount(self.account_data["balance"]), 
                                      fg="white", bg="#0080ff", font=("Arial", 24, "bold"))
        self.balance_display.place(x=20, y=60)
        
        # Liste des transactions
        transaction_frame = tk.Frame(page, bg="white")
        transaction_frame.pack(fill="both", expand=True, padx=10, pady=(160, 10))
        
        transaction_title = tk.Label(transaction_frame, text="Recent Transactions", 
                                    bg="white", font=("Arial", 16, "bold"))
        transaction_title.pack(anchor="w", padx=10, pady=10)
        
        # Canvas pour la liste des transactions avec scrollbar
        transaction_canvas = tk.Canvas(transaction_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(transaction_frame, orient="vertical", command=transaction_canvas.yview)
        self.transaction_list = tk.Frame(transaction_canvas, bg="white")
        
        self.transaction_list.bind("<Configure>", 
                                 lambda e: transaction_canvas.configure(scrollregion=transaction_canvas.bbox("all")))
        
        transaction_canvas.create_window((0, 0), window=self.transaction_list, anchor="nw")
        transaction_canvas.configure(yscrollcommand=scrollbar.set)
        
        transaction_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return page
    
    def create_qpay_page(self):
        page = tk.Frame(self.container, bg="white")
        
        # En-tête
        header = tk.Frame(page, bg="#0080ff", height=50)
        header.pack(fill="x")
        
        back_button = tk.Button(header, text="← Back", bg="#0080ff", fg="white", 
                              bd=0, command=lambda: self.show_page("homePage"))
        back_button.place(x=10, y=15)
        
        title = tk.Label(header, text="QPay", fg="white", bg="#0080ff", font=("Arial", 16, "bold"))
        title.place(relx=0.5, y=15, anchor="center")
        
        # QR Code
        qr_frame = tk.Frame(page, bg="white", padx=20, pady=20)
        qr_frame.pack(fill="both", expand=True)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data("https://qpay.example.com/payment")
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_tk_img = ImageTk.PhotoImage(qr_img)
        
        qr_label = tk.Label(qr_frame, image=qr_tk_img, bg="white")
        qr_label.image = qr_tk_img  # Keep a reference to avoid garbage collection
        qr_label.pack(pady=50)
        qr_label.bind("<Button-1>", lambda e: self.process_qpay_payment())
        
        instructions = tk.Label(qr_frame, text="Click the QR code to make a payment", 
                              bg="white", font=("Arial", 12))
        instructions.pack()
        
        return page
    
    def create_transaction_page(self):
        page = tk.Frame(self.container, bg="white")
        
        # En-tête
        header = tk.Frame(page, bg="#0080ff", height=50)
        header.pack(fill="x")
        
        back_button = tk.Button(header, text="← Back", bg="#0080ff", fg="white", 
                              bd=0, command=lambda: self.show_page("homePage"))
        back_button.place(x=10, y=15)
        
        title = tk.Label(header, text="Transfer", fg="white", bg="#0080ff", font=("Arial", 16, "bold"))
        title.place(relx=0.5, y=15, anchor="center")
        
        # Formulaire de transaction
        form_frame = tk.Frame(page, bg="white", padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)
        
        # Montant
        amount_label = tk.Label(form_frame, text="Amount", bg="white", font=("Arial", 12))
        amount_label.pack(anchor="w", pady=(10, 5))
        
        self.amount_display = tk.Label(form_frame, text="0.00", bg="#f5f5f5", fg="#333", 
                                     font=("Arial", 24, "bold"), width=20, height=2)
        self.amount_display.pack(fill="x", pady=(0, 20))
        self.amount_display.bind("<Button-1>", lambda e: self.show_numeric_keypad())
        
        # Champs de saisie
        fields = [
            {"label": "Recipient Account", "placeholder": "Enter account number"},
            {"label": "Recipient Name", "placeholder": "Enter recipient name"},
            {"label": "Description", "placeholder": "Enter transaction description"}
        ]
        
        self.input_fields = {}
        
        for field in fields:
            label = tk.Label(form_frame, text=field["label"], bg="white", font=("Arial", 12))
            label.pack(anchor="w", pady=(10, 5))
            
            entry = tk.Entry(form_frame, font=("Arial", 12), bg="#f5f5f5", 
                           fg="#333", bd=0, highlightthickness=1, highlightbackground="#ddd")
            entry.insert(0, field["placeholder"])
            entry.pack(fill="x", ipady=8, pady=(0, 10))
            
            # Focus in/out events
            entry.bind("<FocusIn>", lambda e, entry=entry, placeholder=field["placeholder"]: 
                     self.on_entry_focus_in(entry, placeholder))
            entry.bind("<FocusOut>", lambda e, entry=entry, placeholder=field["placeholder"]: 
                      self.on_entry_focus_out(entry, placeholder))
            
            self.input_fields[field["label"]] = entry
        
        # Bouton Continuer
        continue_button = tk.Button(form_frame, text="Continue", bg="#0080ff", fg="white", 
                                  font=("Arial", 14, "bold"), bd=0, padx=20, pady=10,
                                  command=self.process_transfer)
        continue_button.pack(fill="x", pady=20)
        
        return page
    
    def create_confirmation_page(self):
        page = tk.Frame(self.container, bg="white")
        
        # En-tête
        header = tk.Frame(page, bg="#0080ff", height=150)
        header.pack(fill="x")
        
        success_label = tk.Label(header, text="Successfully sent", fg="white", bg="#0080ff", font=("Arial", 16))
        success_label.place(relx=0.5, y=50, anchor="center")
        
        self.success_amount = tk.Label(header, text="0.00 MNT", fg="white", bg="#0080ff", font=("Arial", 24, "bold"))
        self.success_amount.place(relx=0.5, y=90, anchor="center")
        
        # Détails de la transaction
        details_frame = tk.Frame(page, bg="white", padx=20, pady=20)
        details_frame.pack(fill="both", expand=True)
        
        self.transaction_datetime = tk.Label(details_frame, text="", bg="white", font=("Arial", 12))
        self.transaction_datetime.pack(anchor="w", pady=10)
        
        # Lignes de détails
        detail_labels = ["Account Balance", "Recipient", "Account Number", "Description"]
        self.detail_values = []
        
        for label in detail_labels:
            detail_row = tk.Frame(details_frame, bg="white", pady=10)
            detail_row.pack(fill="x")
            
            label_widget = tk.Label(detail_row, text=label, bg="white", fg="#888", font=("Arial", 12))
            label_widget.pack(anchor="w")
            
            value_widget = tk.Label(detail_row, text="", bg="white", font=("Arial", 14, "bold"))
            value_widget.pack(anchor="w", pady=(5, 0))
            
            self.detail_values.append(value_widget)
        
        # Bouton Terminer
        finish_button = tk.Button(details_frame, text="Finish", bg="#0080ff", fg="white", 
                                font=("Arial", 14, "bold"), bd=0, padx=20, pady=10,
                                command=lambda: self.show_page("homePage"))
        finish_button.pack(fill="x", pady=20)
        
        return page
    
    def create_navigation_bar(self):
        nav_bar = tk.Frame(self.root, bg="white", height=60)
        nav_bar.pack(side="bottom", fill="x")
        
        nav_items = [
            {"text": "Home", "icon": "🏠", "page": "homePage"},
            {"text": "QPay", "icon": "📱", "page": "qpayPage"},
            {"text": "Transfer", "icon": "↗️", "page": "transactionPage"}
        ]
        
        self.nav_buttons = []
        
        for i, item in enumerate(nav_items):
            button_frame = tk.Frame(nav_bar, bg="white")
            button_frame.pack(side="left", expand=True, fill="both")
            
            icon = tk.Label(button_frame, text=item["icon"], bg="white", font=("Arial", 24))
            icon.pack(pady=(5, 0))
            
            text = tk.Label(button_frame, text=item["text"], bg="white", font=("Arial", 10))
            text.pack()
            
            # Stocker les références pour la gestion des états actifs
            self.nav_buttons.append((button_frame, icon, text))
            
            # Lier l'événement de clic
            button_frame.bind("<Button-1>", lambda e, page=item["page"]: self.show_page(page))
    
    def show_page(self, page_id):
        # Masquer toutes les pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Afficher la page sélectionnée
        self.pages[page_id].pack(fill="both", expand=True)
        
        # Mettre à jour les éléments actifs dans la navigation
        if page_id == "homePage":
            self.update_active_nav_item("home")
            self.update_home_page_data()
        elif page_id == "qpayPage":
            self.update_active_nav_item("qpay")
        elif page_id == "transactionPage":
            self.update_active_nav_item("transfer")
            self.reset_transfer_form()
    
    def update_active_nav_item(self, active_item):
        for i, (frame, icon, text) in enumerate(self.nav_buttons):
            if (active_item == "home" and i == 0) or \
               (active_item == "qpay" and i == 1) or \
               (active_item == "transfer" and i == 2):
                frame.config(bg="#f0f7ff")
                icon.config(bg="#f0f7ff", fg="#0080ff")
                text.config(bg="#f0f7ff", fg="#0080ff")
            else:
                frame.config(bg="white")
                icon.config(bg="white", fg="black")
                text.config(bg="white", fg="black")
    
    def update_home_page_data(self):
        # Mettre à jour le solde affiché
        self.balance_display.config(text=self.format_amount(self.account_data["balance"]))
        
        # Mettre à jour la liste des transactions
        self.update_transactions_list()
    
    def update_transactions_list(self):
        # Vider la liste des transactions existante
        for widget in self.transaction_list.winfo_children():
            widget.destroy()
        
        # Regrouper les transactions par date
        transactions_by_date = {}
        for transaction in self.account_data["transactions"]:
            if transaction["date"] not in transactions_by_date:
                transactions_by_date[transaction["date"]] = []
            transactions_by_date[transaction["date"]].append(transaction)
        
        # Trier les dates par ordre décroissant (plus récent en premier)
        sorted_dates = sorted(transactions_by_date.keys(), reverse=True)
        
        # Créer les éléments pour chaque date et ses transactions
        for date in sorted_dates:
            # Ajouter la date
            date_label = tk.Label(self.transaction_list, text=date, bg="#f5f5f5", 
                                font=("Arial", 12, "bold"), width=40, anchor="w", padx=10, pady=5)
            date_label.pack(fill="x", pady=(10, 0))
            
            # Ajouter les transactions pour cette date
            for transaction in transactions_by_date[date]:
                self.create_transaction_element(transaction)
    
    def create_transaction_element(self, transaction):
        transaction_frame = tk.Frame(self.transaction_list, bg="white", padx=10, pady=10, width=350)
        transaction_frame.pack(fill="x", pady=2)
        transaction_frame.pack_propagate(False)
        
        # Heure de la transaction
        time_label = tk.Label(transaction_frame, text=transaction["time"], 
                            bg="white", font=("Arial", 10), width=5, anchor="w")
        time_label.grid(row=0, column=0, padx=(0, 10))
        
        # Détails de la transaction
        details_frame = tk.Frame(transaction_frame, bg="white")
        details_frame.grid(row=0, column=1, sticky="nsew")
        
        # Icône selon le type
        icon_text = "↗️" if transaction["type"] == "up" else "📱"
        icon_label = tk.Label(details_frame, text=icon_text, bg="white", font=("Arial", 16))
        icon_label.grid(row=0, column=0, rowspan=2, padx=(0, 10))
        
        # Description et solde restant
        desc_label = tk.Label(details_frame, text=transaction["description"], 
                            bg="white", font=("Arial", 12, "bold"), anchor="w")
        desc_label.grid(row=0, column=1, sticky="w")
        
        rem_label = tk.Label(details_frame, text=f"Rem: {self.format_amount(transaction['remainingBalance'])}", 
                           bg="white", font=("Arial", 10), fg="#888", anchor="w")
        rem_label.grid(row=1, column=1, sticky="w")
        
        # Montant
        amount_text = f"{'' if transaction['amount'] < 0 else '+'}{self.format_amount(transaction['amount'])}"
        amount_color = "red" if transaction["amount"] < 0 else "green"
        amount_label = tk.Label(transaction_frame, text=amount_text, 
                              bg="white", fg=amount_color, font=("Arial", 12, "bold"))
        amount_label.grid(row=0, column=2, padx=(10, 0))
        
        # Configurer l'expansibilité des colonnes
        transaction_frame.columnconfigure(1, weight=1)
    
    def format_amount(self, amount):
        """Fonction pour formater les montants avec séparateur de milliers"""
        return f"{amount:,.2f}"
    
    def format_date(self, date):
        """Fonction pour formater la date au format YYYY.MM.DD"""
        return date.strftime("%Y.%m.%d")
    
    def format_time(self, date):
        """Fonction pour formater l'heure au format HH:MM"""
        return date.strftime("%H:%M")
    
    def reset_transfer_form(self):
        """Fonction pour réinitialiser le formulaire de transfert"""
        self.amount_display.config(text="0.00")
        
        # Réinitialiser les champs de saisie
        for field_name, entry in self.input_fields.items():
            placeholder = f"Enter {field_name.lower()}"
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
            entry.config(fg="#888")
    
    def on_entry_focus_in(self, entry, placeholder):
        """Gérer l'événement de focus d'un champ"""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#333")
    
    def on_entry_focus_out(self, entry, placeholder):
        """Gérer la perte de focus d'un champ"""
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="#888")
    
    def show_numeric_keypad(self):
        """Simulation d'un clavier numérique pour entrer le montant"""
        amount = messagebox.askstring("Montant", "Entrez le montant:", initialvalue=self.amount_display.cget("text"))
        if amount is not None and amount.replace(".", "", 1).isdigit():
            self.amount_display.config(text=self.format_amount(float(amount)))
    
    def process_transfer(self):
        """Fonction pour traiter le transfert"""
        # Récupérer les valeurs du formulaire
        amount_text = self.amount_display.cget("text")
        amount = float(amount_text.replace(",", "")) * -1  # Convertir en négatif car c'est une dépense
        
        recipient_account = self.input_fields["Recipient Account"].get()
        if recipient_account == "Enter account number":
            recipient_account = ""
            
        recipient_name = self.input_fields["Recipient Name"].get()
        if recipient_name == "Enter recipient name":
            recipient_name = ""
        
        description = self.input_fields["Description"].get()
        if description == "Enter transaction description":
            description = "Transfer"
        
        # Vérifier que les champs sont remplis
        if not recipient_account or not recipient_name or amount == 0:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs requis et entrer un montant valide.")
            return
        
        # Vérifier que le solde est suffisant
        if self.account_data["balance"] < abs(amount):
            messagebox.showerror("Erreur", "Solde insuffisant pour effectuer cette transaction.")
            return
        
        # Mettre à jour le solde
        new_balance = self.account_data["balance"] + amount
        
        # Créer une nouvelle transaction
        now = datetime.datetime.now()
        new_transaction = {
            "date": self.format_date(now),
            "time": self.format_time(now),
            "description": description,
            "amount": amount,
            "type": "up",  # Type par défaut pour les transferts
            "remainingBalance": new_balance
        }
        
        # Ajouter la transaction à l'historique
        self.account_data["transactions"].insert(0, new_transaction)
        
        # Mettre à jour le solde du compte
        self.account_data["balance"] = new_balance
        
        # Préparer les données pour la page de confirmation
        self.update_confirmation_page(amount, recipient_name, recipient_account, description)
        
        # Afficher la page de confirmation
        self.show_page("confirmationPage")
    
    def update_confirmation_page(self, amount, recipient_name, recipient_account, description):
        """Fonction pour mettre à jour la page de confirmation"""
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y/%m/%d")
        formatted_time = now.strftime("%H:%M")
        
        # Mettre à jour les informations de la transaction
        self.success_amount.config(text=f"{self.format_amount(abs(amount))} MNT")
        self.transaction_datetime.config(text=f"{formatted_date} {formatted_time}")
        
        # Mettre à jour les détails de la transaction
        # Solde du compte
        self.detail_values[0].config(text=f"{self.format_amount(self.account_data['balance'])} ₮ 👁")
        
        # Destinataire (nom)
        truncated_name = recipient_name[:10] + '...' if len(recipient_name) > 10 else recipient_name
        self.detail_values[1].config(text=f"{truncated_name} ₮")
        
        # Numéro de compte
        self.detail_values[2].config(text=recipient_account)
        
        # Description de la transaction
        self.detail_values[3].config(text=description)
    
    def process_qpay_payment(self):
        """Fonction pour simuler un paiement QPay"""
        amount = messagebox.askstring("QPay", "Entrez le montant du paiement QPay:", initialvalue="0.00")
        
        if amount is None or not amount.replace(".", "", 1).isdigit():
            return
        
        payment_amount = float(amount) * -1  # Convertir en négatif car c'est une dépense
        
        # Vérifier que le solde est suffisant
        if self.account_data["balance"] < abs(payment_amount):
            messagebox.showerror("Erreur", "Solde insuffisant pour effectuer ce paiement.")
            return
        
        # Mettre à jour le solde
        new_balance = self.account_data["balance"] + payment_amount
        
        # Créer une nouvelle transaction
        now = datetime.datetime.now()
        new_transaction = {
            "date": self.format_date(now),
            "time": self.format_time(now),
            "description": "QPay Payment",
            "amount": payment_amount,
            "type": "qr",  # Type pour les paiements QPay
            "remainingBalance": new_balance
        }
        
        # Ajouter la transaction à l'historique
        self.account_data["transactions"].insert(0, new_transaction)
        
        # Mettre à jour le solde du compte
        self.account_data["balance"] = new_balance
        
        # Mettre à jour l'affichage et revenir à la page d'accueil
        messagebox.showinfo("Succès", "Paiement QPay effectué avec succès!")
        self.show_page("homePage")


if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()