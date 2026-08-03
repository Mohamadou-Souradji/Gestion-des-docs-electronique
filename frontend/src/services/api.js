/**
 * Service API centralisé.
 * Toutes les vues et modules importent cette instance
 * au lieu de créer leur propre axios.create().
 */

import axios from 'axios'

const BASE_URL = 'https://gestion-des-docs-electronique.onrender.com/api'
function getToken() {
  return localStorage.getItem('access') || ''
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://gestion-des-docs-electronique.onrender.com/api',
})
// Injecter le token JWT à chaque requête
api.interceptors.request.use(config => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Gérer l'expiration du token globalement
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default api

// Raccourcis pratiques
export const courriersApi = {
  liste:          (params) => api.get('/courriers/', { params }),  // ← MODIFIER
  creer:          (data)   => api.post('/courriers/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  valider:        (id, d)  => api.patch(`/courriers/${id}/valider/`, d),
  rejeter:        (id, d)  => api.patch(`/courriers/${id}/rejeter/`, d),
  imputer:        (id, d)  => api.patch(`/courriers/${id}/imputer/`, d),
  marquerLu:      (id)     => api.patch(`/courriers/${id}/marquer-lu/`),
  archiver:       (id)     => api.patch(`/courriers/${id}/archiver/`),
  marquerTraite: (id, d) => api.patch(`/courriers/${id}/marquer-traite/`, d, { headers: { 'Content-Type': 'multipart/form-data' } }),
  destinataires:  ()       => api.get('/destinataires/'),
  consignes:      ()       => api.get('/consignes-types/'),
  validerSga:  (id, d) => api.patch(`/courriers/${id}/valider-sga/`, d),
  rejeterSga:  (id, d) => api.patch(`/courriers/${id}/rejeter-sga/`, d),
  validerSg:   (id, d) => api.patch(`/courriers/${id}/valider-sg/`, d),
  traiterCopie: (id, d) => api.patch(`/courriers/${id}/traiter-copie/`, d, { headers: { 'Content-Type': 'multipart/form-data' } }),
}

export const archivesApi = {
  liste:      (params) => api.get('/archives/', { params }),
  creer:      (data)   => api.post('/archives/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  fonds:      ()       => api.get('/archives/fonds/'),
}

export const notificationsApi = {
  liste:    () => api.get('/notifications/'),
  compter:  () => api.get('/notifications/count/'),
}

export const usersApi = {
  monProfil:     ()       => api.get('/moi/'),
  liste:         ()       => api.get('/utilisateurs/'),
  creer:         (data)   => api.post('/utilisateurs/creer/', data),
  modifier:      (id, d)  => api.patch(`/utilisateurs/${id}/modifier/`, d),
  basculer:      (id)     => api.patch(`/utilisateurs/${id}/basculer/`),
  deverrouiller: (id)     => api.patch(`/utilisateurs/${id}/deverrouiller/`),
  changerMdp:    (data)   => api.post('/mot-de-passe/', data),
}

export const parametresApi = {
  publics:    ()       => api.get('/parametres/publics/'),
  get:        ()       => api.get('/parametres/'),
  modifier:   (data)   => api.patch('/parametres/', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
}

export const directionsApi = {
  liste:      ()       => api.get('/directions/'),
  creer:      (data)   => api.post('/directions/', data),
  supprimer:  (id)     => api.delete(`/directions/${id}/`),
}

  export const dashboardApi = {
    statistiques: (params) => api.get('/statistiques/', { params }),
    exportExcel:  (params) => api.get('/export/excel/', { params, responseType: 'blob' }),
    exportPdf:    (params) => api.get('/export/pdf/',   { params, responseType: 'blob' }),
    audit:        (params) => api.get('/audit/', { params }),
    recherche:    (params) => api.get('/recherche/', { params }),
    delegations:  ()       => api.get('/delegations/'),
    creerDeleg:   (data)   => api.post('/delegations/', data),
    revoquerDeleg:(id, d)  => api.patch(`/delegations/${id}/revoquer/`, d),
    supervision:  ()       => api.get('/supervision/'),
  }
