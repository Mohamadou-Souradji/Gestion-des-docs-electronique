import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'https://gestion-des-docs-electronique.onrender.com/api'

export function getApiClient() {
  const token = localStorage.getItem('access')
  return axios.create({
    baseURL: API_URL,
    headers: {
      Authorization: token ? `Bearer ${token}` : undefined,
      'Content-Type': 'application/json'
    }
  })
}
