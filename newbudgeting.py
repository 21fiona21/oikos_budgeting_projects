import pandas as pd
import streamlit as st
import psycopg2
import hashlib
import os
import datetime
import boto3

# AWS DynamoDB-Client initialisieren
dynamodb = boto3.resource(
    "dynamodb",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

table_name = "oikos_budgeting"  # Gleicher Tabellenname wie bei der Leitung
table = dynamodb.Table(table_name)

# Benutzer und gehashte Passwörter
users = {
    "oikos_conference": hashlib.sha256(os.getenv("OIKOS_CONFERENCE_PASSWORD").encode()).hexdigest(),
    "oikos_sustainability_week": hashlib.sha256(os.getenv("OIKOS_SUSTAINABILITY_WEEK_PASSWORD").encode()).hexdigest(),
    "oikos_action_days": hashlib.sha256(os.getenv("OIKOS_ACTION_DAYS_PASSWORD").encode()).hexdigest(),
    "oikos_curriculum_change": hashlib.sha256(os.getenv("OIKOS_CURRICULUM_CHANGE_PASSWORD").encode()).hexdigest(),
    "oikos_un-dress": hashlib.sha256(os.getenv("OIKOS_UN_DRESS_PASSWORD").encode()).hexdigest(),
    "oikos_changehub": hashlib.sha256(os.getenv("OIKOS_CHANGEHUB_PASSWORD").encode()).hexdigest(),
    "oikos_solar": hashlib.sha256(os.getenv("OIKOS_SOLAR_PASSWORD").encode()).hexdigest(),
    "oikos_catalyst": hashlib.sha256(os.getenv("OIKOS_CATALYST_PASSWORD").encode()).hexdigest(),
    "oikos_climate_neutral_events": hashlib.sha256(os.getenv("OIKOS_CLIMATE_NEUTRAL_EVENTS_PASSWORD").encode()).hexdigest(),
    "oikos_consulting": hashlib.sha256(os.getenv("OIKOS_CONSULTING_PASSWORD").encode()).hexdigest(),
    "oikos_sustainable_finance": hashlib.sha256(os.getenv("OIKOS_SUSTAINABLE_FINANCE_PASSWORD").encode()).hexdigest(),
    "oikos_oismak": hashlib.sha256(os.getenv("OIKOS_OISMAK_PASSWORD").encode()).hexdigest(),
}

# Zuordnung von Benutzernamen zu Projektnamen
user_names = {
    "oikos_conference": "oikos Conference",
    "oikos_sustainability_week": "Sustainability Week",
    "oikos_action_days": "Action Days",
    "oikos_curriculum_change": "Curriculum Change",
    "oikos_un-dress": "UN-DRESS",
    "oikos_changehub": "ChangeHub",
    "oikos_solar": "oikos Solar",
    "oikos_catalyst": "oikos Catalyst",
    "oikos_climate_neutral_events": "Climate Neutral Events",
    "oikos_consulting": "oikos Consulting",
    "oikos_sustainable_finance": "Sustainable Finance",
    "oikos_oismak": "Oismak"
}

def app():
    project_name = st.session_state["user"]
    
    if project_name == "oikos Conference":
        color = "#4386e8"
    elif project_name == "Sustainability Week":
        color = "#98CE6B"
    elif project_name == "Action Days":
        color = "#DDD5C0"
    elif project_name == "Curriculum Change":
        color = "#EFC9F3"
    elif project_name == "UN-DRESS":
        color = "#A8A8A8"
    elif project_name == "ChangeHub":
        color = "#E7B789"
    elif project_name == "oikos Solar":
        color = "#7686F7"
    elif project_name == "oikos Catalyst":
        color = "#82CBF9"
    elif project_name == "Climate Neutral Events":
        color = "#759272"
    elif project_name == "oikos Consulting":
        color = "#c75f58"
    elif project_name == "Sustainable Finance":
        color = "#DA873C"
    elif project_name == "Oismak":
        color = "#BCC9DD"


    # Funktion zum Einfügen der Daten in die PostgreSQL-Datenbank
    def insert_expense(title, description, date, exact_amount, estimated, conservative, worst_case, priority):
        try:
            # Generiere eine fortlaufende ID
            response = table.scan(ProjectionExpression="id")
            existing_ids = [int(item["id"]) for item in response.get("Items", []) if item["id"].isdigit()]
            expense_id = str(max(existing_ids) + 1) if existing_ids else "1"
    
            # Erstelle das Item mit den richtigen Datentypen
            expense_item = {
                "id": expense_id,
                "project": project_name,
                "title": title,
                "description": description,
                "expense_date": str(date) if date else None,
                "exact_amount": str(exact_amount) if exact_amount else None,
                "estimated": str(estimated) if estimated else None,
                "conservative": str(conservative) if conservative else None,
                "worst_case": str(worst_case) if worst_case else None,
                "priority": int(priority) if priority else None,
                "status": "not assigned"  # Projekte können den Status nicht ändern
            }
    
            # Eintrag in DynamoDB speichern
            table.put_item(Item=expense_item)
            st.success(f"Expense successfully saved!")
    
        except Exception as error:
            st.error(f"Error saving expense: {error}")

    
    # Streamlit Form für die Eingabe
    st.title("Hey oikee!")
    st.subheader(f"Welcome to the oikos budgeting tool. You are logged in as {project_name}")
    st.write("")
    st.write("")

    with st.expander("Instructions"):
        st.markdown("""
        This tool helps you submit upcoming expenses for board approval. Each project is guaranteed funding up to the profit made last semester. However, please submit all foreseeable expenses, not just those exceeding your budget, so the board can allocate funds effectively. This also allows the board to potentially help reduce costs by negotiating better offers or managing expenses collectively.
        
        **Categorizing Expenses:**  
        Group related expenses together where it makes sense. For example, ordering food for an event can be submitted as one expense rather than itemizing each food item. However, different services (e.g., event venue, catering, security, and transport) should be submitted separately, as they come from different providers and have distinct cost structures.
        
        When entering expenses, indicate whether the amount is confirmed or estimated. If it's confirmed (e.g., due to a binding offer or invoice), enter the exact amount. For estimated expenses, provide three values:
        
        * **Estimated:** What you realistically expect the expense to be.
        * **Conservative:** A slightly higher estimate to cover potential variations.
        * **Worst-case:** The maximum amount you might need if things go wrong (e.g., alternative options or last-minute changes).
        
        Finally, indicate whether the expense is tied to a specific date. If it's linked to an event or deadline (e.g., catering for a scheduled event), select "specific date known" and enter the date you need the money by. If the date is unknown, select "Specific date unknown." If the expense is not tied to a date and order(s) can be placed any time during the semester, for example, for general materials, select "Not associated with a specific date."

        **Entering a New Expense:**  
        To add an expense, fill in the mandatory fields for the title and description. Specify if the expense has a known date, and if so, enter it. For exact costs, input the amount directly. For estimated expenses, select "Estimation" and enter the estimated, conservative, and worst-case values.

        Set the priority of your expense (1 being the highest). **Note:** Priority helps you organize your expenses and guides the board’s efforts to optimize overall project spending, but it does not guarantee approval. Be honest in assessing what’s most important for your project.

        After submitting an expense, click on the "Refresh to view changes" button to see your updates.

        **Deleting an Expense:**  
        If you need to delete an expense, enter the ID of the expense and click the "Check" button to view the details. Once confirmed, you can click "Delete" to remove the entry.

        **Expense Submission Deadline:**  
        You can enter and modify expenses until (and including) **March 8, 2025**. After this deadline, you will still be able to view your expenses, but no further changes or submissions will be allowed.
        """)


    st.write("")

    # Festgelegte Deadline (08.03.2025)
    deadline = datetime.date(2025, 3, 8)
    current_date = datetime.date.today()

    # Überprüfen, ob das aktuelle Datum vor oder gleich der Deadline liegt
    if current_date <= deadline:

        st.write("")

        # Verwende einen Container für die Strukturierung
        with st.container():
            st.subheader("Enter an expense")
            
            # Eingabe der Felder
            title = st.text_input("Title of the expense (mandatory)")
            description = st.text_input("Description (mandatory)")
            
            enter_date = st.radio("Is the expense associated with a specific date, and if so, is the date known?", 
                                ("Not associated with a specific date", "specific date unknown", "specific date known"))

            if enter_date == "specific date known":
                date = st.date_input("Enter the (first) date of the expense YYYY-MM-DD").strftime('%Y-%m-%d')  # Formatierung als String
            elif enter_date == "specific date unknown":
                date = "unknown"
            else:
                date = None

        # Zweiter Container für Beträge
        with st.container():
            guaranteed_amount = st.radio("Is the amount of the expense guaranteed (there is a bill or binding offer) or does it have to be estimated?", 
                                        ("Exact amount known", "Estimation"))

            if guaranteed_amount == "Exact amount known":
                exact_amount = st.number_input("Enter the exact amount of the expense in CHF")
                estimated = None
                conservative = None
                worst_case = None
            elif guaranteed_amount == "Estimation":
                exact_amount = None
                col1, col2, col3 = st.columns(3)  # Spalten für die geschätzten Beträge
                with col1:
                    estimated = st.number_input("Estimated amount in CHF")
                with col2:
                    conservative = st.number_input("Conservative estimate in CHF")
                with col3:
                    worst_case = st.number_input("Worst-case amount in CHF")

        # Eingabe für Priorität
        priority = st.number_input("Priority of the expense (1 is the highest priority)", min_value=1, max_value=5)

        # Submit-Button rechtsbündig
        st.markdown("""
            <style>
            .stButton button {
                float: right;
            }
            </style>
            """, unsafe_allow_html=True)

        # Überprüfen, ob beide Pflichtfelder ausgefüllt sind
        if st.button("Submit"):
            if title and description:
                insert_expense(title, description, date, exact_amount, estimated, conservative, worst_case, priority)
                # Füge einen Button hinzu, um die App neu zu laden
                if st.button("Refresh to view changes"):
                    st.rerun()  # Lädt die App neu, ohne dass sich der Benutzer erneut einloggen muss
            else:
                st.error("Both Title and Description are mandatory fields!")

    else:
        st.write(f"The deadline for submitting expenses has passed. No more expenses can be entered after {deadline}.")





    # Funktion zum Laden der Daten aus der Datenbank
    def load_data_from_db():
        try:
            response = table.scan()
            data = response.get("Items", [])
    
            if not data:
                return pd.DataFrame(columns=["id", "project", "title", "description", "expense_date", 
                                             "exact_amount", "estimated", "conservative", "worst_case", "priority", "status"])
    
            # Konvertiere Werte in die richtigen Datentypen
            for item in data:
                if 'exact_amount' in item:
                    item['exact_amount'] = float(item['exact_amount']) if item['exact_amount'] not in [None, ""] else None
                if 'estimated' in item:
                    item['estimated'] = float(item['estimated']) if item['estimated'] not in [None, ""] else None
                if 'conservative' in item:
                    item['conservative'] = float(item['conservative']) if item['conservative'] not in [None, ""] else None
                if 'worst_case' in item:
                    item['worst_case'] = float(item['worst_case']) if item['worst_case'] not in [None, ""] else None
                if 'priority' in item:
                    item['priority'] = int(item['priority']) if item['priority'] not in [None, ""] else None
                if 'id' in item:
                    item['id'] = str(item['id'])
                if 'project' in item:
                    item['project'] = str(item['project'])
                if 'title' in item:
                    item['title'] = str(item['title'])
                if 'description' in item:
                    item['description'] = str(item['description'])
                if 'expense_date' in item:
                    item['expense_date'] = str(item['expense_date'])
                if 'status' in item:
                    item['status'] = str(item['status'])
    
            df = pd.DataFrame(data)
    
            # Fehlende Spalten hinzufügen
            required_columns = ["id", "project", "title", "description", "expense_date", 
                                "exact_amount", "estimated", "conservative", "worst_case", "priority", "status"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
    
            # Setze Datentypen explizit
            df = df.astype({
                "id": str,
                "project": str,
                "title": str,
                "description": str,
                "expense_date": str,
                "exact_amount": "float64",
                "estimated": "float64",
                "conservative": "float64",
                "worst_case": "float64",
                "priority": "Int64",  # Int64 erlaubt auch NaN
                "status": str
            }, errors="ignore")
    
            return df
    
        except Exception as e:
            st.error(f"Error connecting to DynamoDB: {e}")
            return pd.DataFrame()

    

    # Calls DF
    df = load_data_from_db()

    df_projectspecific = df[df['project'] == project_name]

    st.write("")
    st.write("")
    st.write("")

    st.header("Expenses Overview")
    st.write("")

    # Stelle sicher, dass der DataFrame nicht leer ist
    if not df_projectspecific.empty:
        # Durchlaufe alle Einträge im DataFrame
        for i in range(0, len(df_projectspecific), 3):  # Schleife in Schritten von 3

            # Erstelle drei Spalten
            cols = st.columns(3)

            # Für jeden Eintrag in den nächsten drei Daten, fülle die Spalten
            for j, col in enumerate(cols):
                if i + j < len(df_projectspecific):  # Überprüfe, ob der Index gültig ist
                    entry = df_projectspecific.iloc[i + j]
                    
                    if entry['exact_amount'] and entry['exact_amount'] > 0:
                        # Container-Inhalt als HTML-Markdown
                        container_content = f"""
                        <div style='background-color: {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                            <p>id: {entry['id']}</p>
                            <h4>{entry['title']}</h4>
                            <p>{entry['description']}</p>
                            <p><strong>Date: </strong>{entry['expense_date']}</p>
                            <p><strong>Amount:</strong> CHF {entry['exact_amount']}</p>
                            <p><strong>Priority:</strong> {entry['priority']}</p>
                            <p><strong>Status:</strong> {entry['status']}</p>
                        </div>
                        """
                        # Den gesamten Container in der Spalte anzeigen
                        col.markdown(container_content, unsafe_allow_html=True)
                    else:
                        # Container-Inhalt als HTML-Markdown
                        container_content = f"""
                        <div style='background-color: {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                            <p>id: {entry['id']}</p>
                            <h4>{entry['title']}</h4>
                            <p>{entry['description']}</p>
                            <p><strong>Date: </strong>{entry['expense_date']}</p>
                            <p><strong>Amount:</strong> CHF {entry['exact_amount'] if entry['exact_amount'] and entry['exact_amount'] > 0 else (f"{entry['estimated']} / {entry['conservative']} / {entry['worst_case']}" if entry['estimated'] and entry['conservative'] and entry['worst_case'] else 'N/A')}</p>
                            <p><strong>Priority:</strong> {entry['priority']}</p>
                            <p><strong>Status:</strong> {entry['status']}</p>
                        </div>
                        """
                        # Den gesamten Container in der Spalte anzeigen
                        col.markdown(container_content, unsafe_allow_html=True)
    else:
        st.write("No data available for the selected project.")


    st.write("")
    st.write("")
    st.write("")

    # Funktion zum Löschen eines Eintrags aus der PostgreSQL-Datenbank
    def delete_expense_by_id(expense_id):
        try:
            table.delete_item(Key={"id": str(expense_id)})
            st.success(f"Expense successfully deleted!")
            if st.button("Refresh to view changes"):
                st.rerun()
        except Exception as error:
            st.error(f"Error deleting expense: {error}")

    
    if current_date <= deadline:
        # ID-Eingabefeld zum Löschen
        st.write("")
        st.subheader("Delete an expense")
        expense_id_to_delete = st.number_input("Enter the ID of the expense you want to delete", step=1)

        # Verwende Session-State, um den Zustand des überprüften Eintrags zu speichern
        if "checked_expense" not in st.session_state:
            st.session_state["checked_expense"] = None

        # Button "Check" zur Überprüfung des Eintrags
        if st.button("Check"):
            if expense_id_to_delete:
                try:
                    # Verbindung zur Datenbank herstellen
                    connection = psycopg2.connect(
                        host=os.getenv("DB_HOST"),
                        port=os.getenv("DB_PORT"),
                        dbname=os.getenv("DB_NAME"),
                        user=os.getenv("DB_USER"),
                        password=os.getenv("DB_PASSWORD")
                    )
                    cursor = connection.cursor()

                    # SQL-Abfrage, um den Eintrag mit der spezifischen ID und dem eingeloggten Projekt zu finden
                    cursor.execute("SELECT * FROM expenses WHERE id = %s AND project = %s;", (expense_id_to_delete, st.session_state["user"]))
                    entry = cursor.fetchone()
                    
                    if entry:
                        st.session_state["checked_expense"] = entry  # Speichere den Eintrag im Session-State
                    else:
                        st.error(f"No entry found with ID {expense_id_to_delete} for your project")
                except Exception as error:
                    st.error(f"Error fetching expense: {error}")
                finally:
                    if connection:
                        cursor.close()
                        connection.close()

        # Zeige den überprüften Eintrag an, wenn er im Session-State vorhanden ist
        if st.session_state["checked_expense"]:
            entry = st.session_state["checked_expense"]
            container_content = f"""
                <div style='background-color: {color}, padding: 15px; border-radius: 10px; margin-bottom: 10px;'>
                    <p><strong>ID: </strong>{entry[0]}</p>
                    <h4>{entry[2]}</h4>
                    <p>{entry[3]}</p>
                    <p><strong>Date: </strong>{entry[4]}</p>
                    <p><strong>Amount: </strong>CHF {entry[5] if entry[5] is not None else f"{entry[6]} / {entry[7]} / {entry[8]}"}</p>
                    <p><strong>Priority: </strong>{entry[9]}</p>
                    <p><strong>Status: </strong>{entry[10]}</p>
                </div>
                """
            st.markdown(container_content, unsafe_allow_html=True)
            
            # Button zum Löschen anzeigen, nachdem der Eintrag angezeigt wurde
            if st.button("Delete"):
                delete_expense_by_id(expense_id_to_delete)
                # Nach dem Löschen den Eintrag aus dem Session-State entfernen
                st.session_state["checked_expense"] = None
                
                # Füge einen Button hinzu, um die App neu zu laden
                if st.button("Refresh to view changes"):
                    st.rerun()  # Lädt die App neu, ohne dass sich der Benutzer erneut einloggen muss




# Funktion zum Überprüfen des Passworts
def check_password(username, password):
    if username in users:
        return users[username] == hashlib.sha256(password.encode()).hexdigest()
    return False

# Login-Funktion
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if check_password(username, password):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["user"] = user_names[username] 
            # Seite sofort neu laden
            st.rerun()  # Verwende st.rerun() um die Seite neu zu laden
        else:
            st.error("Incorrect username or password")


# Hauptanwendung
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    app()  # Starte die Hauptanwendung, wenn der Benutzer eingeloggt ist
else:
    login()  # Zeige die Login-Seite, wenn der Benutzer nicht eingeloggt ist
