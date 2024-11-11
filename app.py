import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File path for storing transaction data
DATA_FILE = "transactions.csv"

# Initialize or load transaction data
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Create a new DataFrame if no file exists
        return pd.DataFrame(columns=["person", "action", "amount", "date", "transaction_id"])

# Save transaction data to CSV
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Calculate balances based on transaction history
def calculate_balances(data):
    person1_balance = data[data['person'] == "Person 1"].apply(
        lambda row: row['amount'] if row['action'] == "Credit" else -row['amount'], axis=1).sum()
    person2_balance = data[data['person'] == "Person 2"].apply(
        lambda row: row['amount'] if row['action'] == "Credit" else -row['amount'], axis=1).sum()
    return person1_balance, person2_balance

# Load existing data
data = load_data()

# Calculate initial balances
person1_balance, person2_balance = calculate_balances(data)

# Title
st.title("Shared Bank Account Manager")

# Input form for adding transactions
st.header("Enter Transaction")
with st.form(key="transaction_form_1"):  # Unique key for this form
    person = st.selectbox("Select Person", ["Person 1", "Person 2"])
    action = st.selectbox("Action", ["Credit", "Debit"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    submit = st.form_submit_button("Submit")

# Add transaction to data
if submit:
    # Get current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a unique transaction ID
    transaction_id = len(data) + 1
    
    # Add new transaction to DataFrame
    new_transaction = pd.DataFrame({
        "person": [person],
        "action": [action],
        "amount": [amount],
        "date": [current_date],
        "transaction_id": [transaction_id]
    })
    
    data = pd.concat([data, new_transaction], ignore_index=True)
    save_data(data)
    
    # Recalculate balances
    person1_balance, person2_balance = calculate_balances(data)
    st.success("Transaction recorded successfully!")

# Display balances
st.header("Live Balances")
st.write(f"**Person 1 Balance:** ${person1_balance:.2f}")
st.write(f"**Person 2 Balance:** ${person2_balance:.2f}")
combined_balance = person1_balance + person2_balance
st.write(f"**Combined Balance:** ${combined_balance:.2f}")

# Transaction Details Filter
st.header("Filter Transaction Details")

# Filters
filter_by = st.radio("Filter by", ["None", "Transaction ID", "Date", "Person"])

if filter_by == "Transaction ID":
    transaction_id_filter = st.number_input("Enter Transaction ID", min_value=1, step=1)
    filtered_data = data[data['transaction_id'] == transaction_id_filter]
elif filter_by == "Date":
    date_filter = st.date_input("Select Date")
    filtered_data = data[data['date'].str.startswith(str(date_filter))]
elif filter_by == "Person":
    person_filter = st.selectbox("Select Person", ["Person 1", "Person 2"])
    filtered_data = data[data['person'] == person_filter]
else:
    filtered_data = data

# Display filtered transaction details
if not filtered_data.empty:
    st.subheader("Transaction Details")
    st.write(filtered_data)
else:
    st.write("No transactions found with the selected filters.")

# Transaction update section
st.header("Update or Delete Transaction")

# Select transaction to update or delete
transaction_to_edit = st.selectbox("Select Transaction to Edit/Delete", data['transaction_id'].values)

# Display transaction details
selected_transaction = data[data['transaction_id'] == transaction_to_edit]

if selected_transaction.empty:
    st.write("No transaction selected.")
else:
    st.write(f"Transaction Details: {selected_transaction.iloc[0]}")
    
    with st.form(key="update_form"):
        new_action = st.selectbox("Action", ["Credit", "Debit"], key="update_action")
        new_amount = st.number_input("Amount", min_value=0.0, step=0.01, value=selected_transaction["amount"].iloc[0])
        submit_update = st.form_submit_button("Update Transaction")
        submit_delete = st.form_submit_button("Delete Transaction")
    
    # Update Transaction
    if submit_update:
        data.loc[data['transaction_id'] == transaction_to_edit, 'action'] = new_action
        data.loc[data['transaction_id'] == transaction_to_edit, 'amount'] = new_amount
        save_data(data)
        person1_balance, person2_balance = calculate_balances(data)
        st.success("Transaction updated successfully!")

    # Delete Transaction
    if submit_delete:
        data = data[data['transaction_id'] != transaction_to_edit]
        save_data(data)
        person1_balance, person2_balance = calculate_balances(data)
        st.success("Transaction deleted successfully!")
