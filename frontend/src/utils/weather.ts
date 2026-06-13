import axios from "axios";

export async function fetchWeather(lat: number, lon: number) {
  const response = await axios.get(`https://api.ambeedata.com/weather/latest/by-lat-lng`, {
    params: { lat, lng: lon },
    headers: { "x-api-key": "9d6b3ef390a3e60a5aed9eb8e12c9bc0df6c6795ffbab8183e8484c27d5f9a05" }
  });
  return response.data;
}
