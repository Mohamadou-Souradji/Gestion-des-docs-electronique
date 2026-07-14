import axios from 'axios'

export function getApiClient() {
  const token = localStorage.getItem('access')
  return axios.create({
    baseURL: 'http://localhost:8000/api',
    headers: {
      Authorization: token ? `Bearer ${token}` : undefined,
      'Content-Type': 'application/json'
    }
  })
}
