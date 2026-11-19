// Made by: Hazzard
// Odin Weather App - Open-Meteo client (free, no API key). Returns only the fields the app needs.

const GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search";
const FORECAST_URL = "https://api.open-meteo.com/v1/forecast";

// Expected failures the user can act on; anything else is a bug and gets logged.
export class NetworkError extends Error {}
export class PlaceNotFoundError extends Error {}

async function getJson(url) {
  let response;
  try {
    response = await fetch(url);
  } catch {
    throw new NetworkError("Could not reach the weather service. Check your connection.");
  }
  if (!response.ok) throw new Error(`Weather service answered ${response.status}.`);
  return response.json();
}

export async function findPlace(query) {
  const url = `${GEOCODE_URL}?${new URLSearchParams({ name: query, count: "1", language: "en", format: "json" })}`;
  const data = await getJson(url);
  const place = data.results?.[0];
  if (!place) throw new PlaceNotFoundError(`No place found for "${query}".`);
  return { name: place.name, region: place.admin1 ?? "", country: place.country ?? "", latitude: place.latitude, longitude: place.longitude };
}

export async function getForecast({ latitude, longitude }, unit) {
  const params = new URLSearchParams({
    latitude: String(latitude),
    longitude: String(longitude),
    current: "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day",
    daily: "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
    timezone: "auto",
    forecast_days: "5",
    temperature_unit: unit === "F" ? "fahrenheit" : "celsius",
    wind_speed_unit: unit === "F" ? "mph" : "kmh",
  });
  const data = await getJson(`${FORECAST_URL}?${params}`);
  if (!data.current || !data.daily || !data.current_units) throw new Error("The forecast came back incomplete.");
  return {
    current: {
      temperature: data.current.temperature_2m,
      feelsLike: data.current.apparent_temperature,
      humidity: data.current.relative_humidity_2m,
      wind: data.current.wind_speed_10m,
      code: data.current.weather_code,
      isDay: data.current.is_day === 1,
      time: data.current.time,
    },
    daily: data.daily.time.map((date, i) => ({
      date,
      code: data.daily.weather_code[i],
      max: data.daily.temperature_2m_max[i],
      min: data.daily.temperature_2m_min[i],
      rain: data.daily.precipitation_probability_max?.[i] ?? null,
    })),
    units: { temp: data.current_units.temperature_2m, wind: data.current_units.wind_speed_10m },
  };
}

// WMO weather codes grouped into the few looks the UI has.
export function describe(code) {
  if (code === 0) return { text: "Clear sky", look: "clear" };
  if (code <= 3) return { text: ["Mainly clear", "Partly cloudy", "Overcast"][code - 1], look: "cloudy" };
  if (code === 45 || code === 48) return { text: "Fog", look: "cloudy" };
  if (code >= 51 && code <= 67) return { text: code < 61 ? "Drizzle" : "Rain", look: "rain" };
  if (code >= 71 && code <= 77) return { text: "Snow", look: "snow" };
  if (code >= 80 && code <= 82) return { text: "Rain showers", look: "rain" };
  if (code >= 85 && code <= 86) return { text: "Snow showers", look: "snow" };
  if (code >= 95) return { text: "Thunderstorm", look: "storm" };
  return { text: `Weather code ${code}`, look: "cloudy" };
}
