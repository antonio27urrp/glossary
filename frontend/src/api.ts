const API_URL = "http://localhost:8000";

export const fetchTerms = async () => {
  const response = await fetch(`${API_URL}/terms`);
  if (!response.ok) throw new Error("Ошибка при загрузке данных");
  return response.json();
};