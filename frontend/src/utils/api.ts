// src/utils/api.ts
import axios from "axios";

const API_BASE = "http://localhost:8000"; // Update if deployed

export const predictDisease = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const res = await axios.post(`${API_BASE}/predict-disease/`, formData);
  return res.data;
};

export const recommendCrop = async (formValues: Record<string, any>) => {
  const res = await axios.post(`${API_BASE}/recommend-crop/`, formValues);
  return res.data;
};
