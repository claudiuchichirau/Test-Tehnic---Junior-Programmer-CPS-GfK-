from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Configurare SQLAlchemy pentru SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

API_KEY = "3a01c7b499b3498d94183711242908"

class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    max_temp = db.Column(db.Float, nullable=False)
    min_temp = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float, nullable=False)
    sunrise = db.Column(db.String(5), nullable=False)
    sunset = db.Column(db.String(5), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('date', 'city', name='uix_date_city'),
    )

def get_weather_forecast(city):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=3"

    try:
        response = requests.get(url)    
        response.raise_for_status() # arunca exceptie daca statusul nu e 200
        data = response.json()

        if "forecast" not in data:
            raise ValueError("Invalid response from weather API")

        forecast = []
        if "forecast" in data:
            for day in data['forecast']['forecastday']:
                weather_entry = {
                    'date': day['date'],
                    'max_temp': day['day']['maxtemp_c'],
                    'min_temp': day['day']['mintemp_c'],
                    'precipitation': day['day']['totalprecip_mm'],
                    'sunrise': day['astro']['sunrise'],
                    'sunset': day['astro']['sunset']
                }
                forecast.append(weather_entry)

                try:
                    # se inlocuiesc datelor existente dacs exista deja
                    existing_entry = Weather.query.filter_by(date=day['date'], city=city).first()
                    if existing_entry:
                        existing_entry.max_temp = weather_entry['max_temp']
                        existing_entry.min_temp = weather_entry['min_temp']
                        existing_entry.precipitation = weather_entry['precipitation']
                        existing_entry.sunrise = weather_entry['sunrise']
                        existing_entry.sunset = weather_entry['sunset']
                    else:
                        # se aduaga noi date dacă nu exista deja
                        new_entry = Weather(    
                            date=day['date'],
                            city=city,
                            max_temp=weather_entry['max_temp'],
                            min_temp=weather_entry['min_temp'],
                            precipitation=weather_entry['precipitation'],
                            sunrise=weather_entry['sunrise'],
                            sunset=weather_entry['sunset']
                        )
                        db.session.add(new_entry)
                    db.session.commit()
                except SQLAlchemyError as db_error: # eroari legate de interactiunea cu baza de date (prob. de conectivitate, etc.)
                    db.session.rollback()  # Rollback in case of an error
                    print(f"Database error: {db_error}")
                    flash(f"Error saving weather data for {day['date']} in {city}.", "error")
            db.session.commit()
        return forecast
    except RequestException as req_error: # eroari legate de cererea HTTP (probleme de conexiune, rasp. eronate)
        print(f"API request error: {req_error}")
        flash("Error retrieving data from the weather API. Please try again later.", "error")
        return []
    except ValueError as val_error: # datele primite de la API nu sunt în formatul așteptat.
        print(f"API response error: {val_error}")
        flash("Invalid response from the weather API.", "error")
        return []
    except Exception as e:  # orice alta exceptie negestionata anterior
        print(f"Unexpected error: {e}")
        flash("An unexpected error occurred.", "error")
        return []

@app.route("/", methods=["GET", "POST"])
def home():
    city_name = ""
    weather_data = []
    if request.method == "POST":
        city_name = request.form.get("city")
        weather_data = get_weather_forecast(city_name)

    return render_template("index.html", city=city_name, weather_data=weather_data)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
