import requests
import time
from datetime import datetime, timedelta
from collections import Counter
from models import db, WeatherData, WeatherSummary, WeatherAlert
import matplotlib.pyplot as plt
import io
import base64

class WeatherMonitor:
    def __init__(self, api_key, cities, update_interval=300):
        self.api_key = api_key
        self.cities = cities
        self.update_interval = update_interval
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather_data(self, city):
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {
                "city": city,
                "main": data["weather"][0]["main"],
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "timestamp": datetime.utcfromtimestamp(data["dt"])
            }
        else:
            print(f"Error fetching data for {city}: {response.status_code}")
            return None

    def save_weather_data(self, data):
        weather_data = WeatherData(**data)
        db.session.add(weather_data)
        db.session.commit()

    def calculate_daily_summary(self, city, date):
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        data = WeatherData.query.filter(
            WeatherData.city == city,
            WeatherData.timestamp >= start_date,
            WeatherData.timestamp < end_date
        ).all()

        if not data:
            return None

        temps = [d.temp for d in data]
        conditions = [d.main for d in data]

        summary = WeatherSummary(
            city=city,
            date=date.date(),
            avg_temp=sum(temps) / len(temps),
            max_temp=max(temps),
            min_temp=min(temps),
            dominant_condition=Counter(conditions).most_common(1)[0][0]
        )

        db.session.add(summary)
        db.session.commit()

        return summary

    def check_alert_thresholds(self, data, thresholds):
        alerts = []
        for threshold in thresholds:
            if threshold["type"] == "temperature":
                if data["temp"] > threshold["value"]:
                    alerts.append(WeatherAlert(
                        city=data["city"],
                        alert_type="High Temperature",
                        message=f"Temperature ({data['temp']}°C) exceeds threshold of {threshold['value']}°C"
                    ))
            elif threshold["type"] == "condition":
                if data["main"].lower() == threshold["value"].lower():
                    alerts.append(WeatherAlert(
                        city=data["city"],
                        alert_type="Weather Condition",
                        message=f"Current weather condition ({data['main']}) matches alert condition"
                    ))

        for alert in alerts:
            db.session.add(alert)
        db.session.commit()

        return alerts

    def generate_temperature_chart(self, city, days=7):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        summaries = WeatherSummary.query.filter(
            WeatherSummary.city == city,
            WeatherSummary.date >= start_date.date(),
            WeatherSummary.date <= end_date.date()
        ).order_by(WeatherSummary.date).all()

        dates = [summary.date for summary in summaries]
        avg_temps = [summary.avg_temp for summary in summaries]
        max_temps = [summary.max_temp for summary in summaries]
        min_temps = [summary.min_temp for summary in summaries]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, avg_temps, label='Average')
        plt.plot(dates, max_temps, label='Max')
        plt.plot(dates, min_temps, label='Min')
        plt.title(f'Temperature Trends for {city} (Last {days} Days)')
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.legend()
        plt.grid(True)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def run(self, thresholds):
        while True:
            for city in self.cities:
                data = self.get_weather_data(city)
                if data:
                    self.save_weather_data(data)
                    self.check_alert_thresholds(data, thresholds)
                    self.calculate_daily_summary(city, data["timestamp"])
            time.sleep(self.update_interval)
