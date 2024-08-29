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
    response = requests.get(url)
    data = response.json()

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
    return forecast

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
