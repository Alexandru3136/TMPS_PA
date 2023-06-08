import tkinter as tk
import time
import requests


class Observer:
    """
    Interfață pentru obiectele observator
    """

    def update(self):
        """
        Metodă apelată pentru a actualiza observatorul cu cele mai recente informații
        """


class WeatherFetcher:
    """
    Clasă responsabilă cu preluarea informațiilor despre vreme de la API
    """
    _instance = None

    @staticmethod
    def get_instance(api_key):
        """
        Metodă statică pentru obținerea instanței unice a clasei WeatherFetcher
        """
        if WeatherFetcher._instance is None:
            WeatherFetcher._instance = WeatherFetcher(api_key)
        return WeatherFetcher._instance

    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, city):
        """
        Obține informații despre vreme pentru un oraș dat
        """
        api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}"

        try:
            json_data = requests.get(api_url, timeout=5).json()
            return WeatherData(json_data)
        except requests.exceptions.RequestException:
            return None


class WeatherData:
    """
    Clasă care stochează datele despre vreme
    """

    def __init__(self, json_data):
        self.condition = json_data['weather'][0]['main']
        self.temp = int(json_data['main']['temp'] - 273.15)
        self.min_temp = int(json_data['main']['temp_min'] - 273.15)
        self.max_temp = int(json_data['main']['temp_max'] - 273.15)
        self.pressure = json_data['main']['pressure']
        self.humidity = json_data['main']['humidity']
        self.wind = json_data['wind']['speed']
        self.sunrise = time.strftime('%H:%M:%S', time.gmtime(json_data['sys']['sunrise'] + 10800))
        self.sunset = time.strftime('%H:%M:%S', time.gmtime(json_data['sys']['sunset'] + 10800))


class WeatherDataProvider:
    """
    Interfață pentru furnizorii de date despre vreme
    """

    def get_weather(self, city):
        """
        Obține informații despre vreme pentru un oraș dat
        """
       

    def register_observer(self, observer):
        """
        Înregistrează un obiect observator
        """
       

    def remove_observer(self, observer):
        """
        Elimină un obiect observator
        """
       


class OpenWeatherMapDataProvider(WeatherDataProvider):
    """
    Clasă care implementează interfața WeatherDataProvider și preia datele despre vreme de la API-ul OpenWeatherMap
    """

    def __init__(self, api_key):
        super().__init__()
        self.observers = []
        self.weather_fetcher = WeatherFetcher.get_instance(api_key)

    def register_observer(self, observer):
        """
        Înregistrează un obiect observator
        """
        self.observers.append(observer)

    def remove_observer(self, observer):
        """
        Elimină un obiect observator
        """
        self.observers.remove(observer)

    def notify_observers(self):
        """
        Notifică toți observatorii înregistrați
        """
        for observer in self.observers:
            observer.update()

    def get_weather(self, city):
        """
        Obține informații despre vreme pentru un oraș dat
        """
        return self.weather_fetcher.get_weather(city)


class WeatherApp(tk.Tk, Observer):
    """
    Aplicație pentru prognoza meteo
    """

    def __init__(self, weather_data_provider):
        super().__init__()
        self.geometry("600x500")
        self.title("Weather App")
        self.font_large = ("poppins", 35, "bold")
        self.font_small = ("poppins", 15, "bold")
        self.weather_data_provider = weather_data_provider

        self.text_field = tk.Entry(self, justify='center', width=20, font=self.font_large)
        self.text_field.pack(pady=20)

        self.button = tk.Button(self, text="Caută", command=self.get_weather_info, font=self.font_small)
        self.button.pack(pady=10)

        self.label1 = tk.Label(self, text="", font=self.font_small)
        self.label1.pack(pady=20)

        self.label2 = tk.Label(self, text="", font=self.font_small)
        self.label2.pack(pady=20)

        # Se înregistrează ca observator
        self.weather_data_provider.register_observer(self)

    def update(self):
        """
        Actualizează informațiile despre vreme în interfața grafică
        """
        city = self.text_field.get()
        weather_data = self.weather_data_provider.get_weather(city)

        if weather_data:
            final_info = f"Condiții: {weather_data.condition}\nTemperatură: {weather_data.temp}°C\n" \
                         f"Temperatură Min/Max: {weather_data.min_temp}°C / {weather_data.max_temp}°C\n" \
                         f"Presiune: {weather_data.pressure} hPa\nUmiditate: {weather_data.humidity}%\n" \
                         f"Vânt: {weather_data.wind} m/s\nRăsărit: {weather_data.sunrise}\nApus: {weather_data.sunset}"
            final_data = ""
        else:
            final_info = "Eroare: Nu s-au putut obține datele despre vreme."
            final_data = ""

        self.label1.config(text=final_info)

    def get_weather_info(self):
        """
        Obține informații despre vreme pentru orașul introdus și le afișează în interfața grafică
        """
        city = self.text_field.get()
        self.weather_data_provider.notify_observers()


class WeatherInfoDecorator(WeatherDataProvider):
    """
    Decorator pentru adăugarea unor informații suplimentare la datele despre vreme
    """

    def __init__(self, weather_data_provider):
        self.weather_data_provider = weather_data_provider
        self.observers = []

    def get_weather(self, city):
        """
        Obține informații despre vreme pentru un oraș dat și adaugă informații suplimentare
        """
        weather_data = self.weather_data_provider.get_weather(city)

        if weather_data:
            # Adăugăm informații suplimentare
            weather_data.additional_info = "Aceasta este o informație suplimentară adăugată de decorator."

        return weather_data

    def register_observer(self, observer):
        """
        Înregistrează un obiect observator
        """
        self.observers.append(observer)
        self.weather_data_provider.register_observer(observer)

    def remove_observer(self, observer):
        """
        Elimină un obiect observator
        """
        self.observers.remove(observer)
        self.weather_data_provider.remove_observer(observer)

    def notify_observers(self):
        """
        Notifică toți observatorii înregistrați
        """
        self.weather_data_provider.notify_observers()


if __name__ == "__main__":
    api_key = "06c921750b9a82d8f5d1294e1586276f"
    provider_type = "OpenWeatherMap"  # Specifică tipul dorit de furnizor de date despre vreme

    base_provider = OpenWeatherMapDataProvider(api_key)
    decorated_provider = WeatherInfoDecorator(base_provider)

    app = WeatherApp(decorated_provider)
    app.mainloop()
    