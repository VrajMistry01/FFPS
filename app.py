import datetime
import pickle
import secrets
import mysql.connector
import pandas as pd
from flask import Flask,  render_template, request, session
from flask_cors import cross_origin

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
print(app.secret_key)

model = pickle.load(open("flightpredict_rf1.pkl", "rb"))


@app.route("/")
@cross_origin()
def index():
    return render_template("index.html")


@app.route("/home")
@cross_origin()
def home():
    return render_template("home.html")


@app.route("/register_m", methods=["GET", "POST"])
def register_m():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Set connection variables
        db_host = "localhost"
        db_user = "root"
        db_password = ""
        db_name = "ffps_db"

        # Create a database connection
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        # Check for connection success
        if db.is_connected():
            cursor = db.cursor()
            # Prepare SQL statement and data
            select_sql = "SELECT * FROM records WHERE USERNAME = %s OR EMAIL = %s"
            select_data = (username, email)
            cursor.execute(select_sql, select_data)
            existing_user = cursor.fetchone()

            # Check if user already exists in database
            if existing_user:
                return render_template('register.html', error="Username or email already exists")
            else:
                insert_sql = "INSERT INTO records (USERNAME, EMAIL, PASSWORD) VALUES (%s, %s, %s)"
                insert_data = (username, email, password)
                cursor.execute(insert_sql, insert_data)
                db.commit()
                cursor.close()
                db.close()
                return render_template("login.html")
        else:
            # Failed to connect to database
            return "Failed to connect to database"
    else:
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login_m():
    if request.method == 'POST':
        # Get form data
        email = request.form['email']
        password = request.form['password']
        # Set connection variables
        db_host = "localhost"
        db_user = "root"
        db_password = ""
        db_name = "ffps_db"

        # Create a database connection
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        # Verify email and password from database
        if db.is_connected():

            cur = db.cursor()
            cur.execute(
                'SELECT * FROM records WHERE EMAIL = %s AND PASSWORD = %s', (email, password))
            user = cur.fetchone()

            if user:
                # Redirect to index.html if user is authenticated

                username = user[1]
                session['username'] = username
                return render_template('home.html', username=username)
            else:
                # Show error message if user is not authenticated
                error = 'Invalid email or password'
                return render_template('login.html', error=error)
            # Close the cursor
        cur.close()
        # Commit the transaction
        db.commit()
        # Close the database connection
        db.close()

    # Show login form
    return render_template('login.html')


@app.route("/register")
@cross_origin()
def register():
    return render_template("register.html")


@app.route("/login")
@cross_origin()
def login():
    return render_template("login.html")


@app.route("/History")
@cross_origin()
def History():
    db_host = "localhost"
    db_user = "root"
    db_password = ""
    db_name = "ffps_db"

    # Create a database connection
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    # Create a cursor object
    cursor = db.cursor()

    # Build the SQL query
    username = session.get('username')
    query = "SELECT * FROM search_history WHERE username=%s"
    values = (username,)

    # Execute the query using the cursor
    cursor.execute(query, values)

    # Fetch the results from the cursor
    records = cursor.fetchall()

    # Pass the records and username to the HTML template
    return render_template('history.html', records=records, username=username)


@app.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":
        # Date_of_Journey
        date_dep = request.form["Dep_Time"]
        dep_time = datetime.datetime.strptime(date_dep, "%Y-%m-%dT%H:%M")
        Journey_Day = int(pd.to_datetime(
            date_dep, format="%Y-%m-%dT%H:%M").day)
        Journey_Month = int(pd.to_datetime(
            date_dep, format="%Y-%m-%dT%H:%M").month)

        # Departure
        dep_hour = int(pd.to_datetime(date_dep, format="%Y-%m-%dT%H:%M").hour)
        dep_minute = int(pd.to_datetime(
            date_dep, format="%Y-%m-%dT%H:%M").minute)

        # Arrival
        date_arrival = request.form["Arrival_Time"]
        arr_time = datetime.datetime.strptime(date_arrival, "%Y-%m-%dT%H:%M")
        arrival_hour = int(pd.to_datetime(
            date_arrival, format="%Y-%m-%dT%H:%M").hour)
        arrival_minute = int(pd.to_datetime(
            date_arrival, format="%Y-%m-%dT%H:%M").minute)

        # Duration
        journey_duration = arr_time - dep_time
        total_minutes = int(journey_duration.total_seconds() / 60)
        dur_hour = int(total_minutes / 60)
        dur_min = total_minutes % 60

        # Total Stops
        Total_Stops = int(request.form["Total_Stops"])

        # Airlines

        airline = request.form['Airline']
        if (airline == 'Jet Airways'):
            Jet_Airways = 1
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'IndiGo'):
            Jet_Airways = 0
            IndiGo = 1
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'Air India'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 1
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'Multiple carriers'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 1
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'SpiceJet'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 1
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'Vistara'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 1
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'GoAir'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 1
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'Multiple carriers Premium economy'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 1
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'Jet Airways Business'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 1
            Vistara_Premium_economy = 0
            Trujet = 0

        elif (airline == 'Vistara Premium economy'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 1
            Trujet = 0

        elif (airline == 'Trujet'):
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 1

        else:
            Jet_Airways = 0
            IndiGo = 0
            Air_India = 0
            Multiple_carriers = 0
            SpiceJet = 0
            Vistara = 0
            GoAir = 0
            Multiple_carriers_Premium_economy = 0
            Jet_Airways_Business = 0
            Vistara_Premium_economy = 0
            Trujet = 0

        # Source

        Source = request.form["Source"]
        if (Source == 'Delhi'):
            source_Delhi = 1
            source_Kolkata = 0
            source_Mumbai = 0
            source_Cochin = 0
            source_Banglore = 0

        elif (Source == 'Kolkata'):
            source_Delhi = 0
            source_Kolkata = 1
            source_Mumbai = 0
            source_Cochin = 0
            source_Banglore = 0

        elif (Source == 'Mumbai'):
            source_Delhi = 0
            source_Kolkata = 0
            source_Mumbai = 1
            source_Cochin = 0
            source_Banglore = 0

        elif (Source == 'Cochin'):
            source_Delhi = 0
            source_Kolkata = 0
            source_Mumbai = 0
            source_Cochin = 1
            source_Banglore = 0
        elif (Source == 'Banglore'):
            source_Delhi = 0
            source_Kolkata = 0
            source_Mumbai = 0
            source_Cochin = 0
            source_Banglore = 1

        else:
            source_Delhi = 0
            source_Kolkata = 0
            source_Mumbai = 0
            source_Cochin = 0
            source_Banglore = 0

        # Destination
        Destination = request.form["Destination"]
        if (Source == 'Cochin'):
            destination_Cochin = 1
            destination_Delhi = 0
            destination_New_Delhi = 0
            destination_Hyderabad = 0
            destination_Kolkata = 0
            destination_Banglore = 0

        elif (Destination == 'Delhi'):
            destination_Cochin = 0
            destination_Delhi = 1
            destination_New_Delhi = 0
            destination_Hyderabad = 0
            destination_Kolkata = 0
            destination_Banglore = 0

        elif (Destination == 'New_Delhi'):
            destination_Cochin = 0
            destination_Delhi = 0
            destination_New_Delhi = 1
            destination_Hyderabad = 0
            destination_Kolkata = 0
            destination_Banglore = 0

        elif (Destination == 'Hyderabad'):
            destination_Cochin = 0
            destination_Delhi = 0
            destination_New_Delhi = 0
            destination_Hyderabad = 1
            destination_Kolkata = 0
            destination_Banglore = 0

        elif (Destination == 'Kolkata'):
            destination_Cochin = 0
            destination_Delhi = 0
            destination_New_Delhi = 0
            destination_Hyderabad = 0
            destination_Kolkata = 1
            destination_Banglore = 0

        elif (Destination == 'Banglore'):
            destination_Cochin = 0
            destination_Delhi = 0
            destination_New_Delhi = 0
            destination_Hyderabad = 0
            destination_Kolkata = 0
            destination_Banglore = 1

        else:
            destination_Cochin = 0
            destination_Delhi = 0
            destination_New_Delhi = 0
            destination_Hyderabad = 0
            destination_Kolkata = 0
            destination_Banglore = 0

        prediction = model.predict([[
            Total_Stops,
            Journey_Day,
            Journey_Month,
            dep_hour,
            dep_minute,
            arrival_hour,
            arrival_minute,
            dur_hour,
            dur_min,
            Jet_Airways,
            IndiGo,
            Air_India,
            Multiple_carriers,
            SpiceJet,
            Vistara,
            GoAir,
            Multiple_carriers_Premium_economy,
            Jet_Airways_Business,
            Vistara_Premium_economy,
            Trujet,
            source_Banglore,
            source_Cochin,
            source_Delhi,
            source_Kolkata,
            source_Mumbai,
            destination_Banglore,
            destination_Cochin,
            destination_Delhi,

            destination_Hyderabad, destination_Kolkata,
            destination_New_Delhi


        ]])

        output = round(prediction[0], 2)
        data = {"Source": [Source], 'Destination': [Destination],
                'date_dep': [date_dep],
                'date_arrival': [date_arrival],
                'Journey_Day': [Journey_Day],
                'Journey_Month': [Journey_Month],
                'dep_hour': [dep_hour],
                'dep_minute': [dep_minute],
                'arrival_hour': [arrival_hour],
                'arrival_minute': [arrival_minute],
                'dur_hour': [dur_hour],
                'dur_min': [dur_min],
                'Total_Stops': [Total_Stops],
                'Airline': [airline],
                'Predicted Price': [output]}
        # Set connection variables
        db_host = "localhost"
        db_user = "root"
        db_password = ""
        db_name = "ffps_db"

        # Create a database connection
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        username = session.get('username')
        print(username)

# Get a cursor object
        mycursor = mydb.cursor()
        sql = "INSERT INTO `search_history` (`id`, `username`, `source`, `destination`, `date_dep`, `date_arrival`, `journey_day`, `journey_month`, `dep_hour`, `dep_minute`, `arrival_hour`, `arrival_minute`, `dur_hour`, `dur_min`, `total_stops`, `airline`, `predicted_price`, `created_at`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, current_timestamp());"
        val = (username, Source, Destination, date_dep, date_arrival, Journey_Day, Journey_Month, dep_hour,
               dep_minute, arrival_hour, arrival_minute, dur_hour, dur_min, Total_Stops, airline, output)
        mycursor.execute(sql, val)
        mydb.commit()
        return render_template('response.html', d_d_and_t=date_dep, a_d_and_t=date_arrival, Source=Source, Destination=Destination, Stops=Total_Stops, Airline=airline, Duration="{} hours {} minutes".format(dur_hour, dur_min), prediction_text=output, username=session.get('username'))

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
