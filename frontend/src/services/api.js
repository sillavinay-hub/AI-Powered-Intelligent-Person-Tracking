const API_BASE_URL = '';

class ApiService {
  getToken() {
    return localStorage.getItem('rv_token') || '';
  }

  setToken(token, role, username) {
    localStorage.setItem('rv_token', token);
    localStorage.setItem('rv_role', role);
    localStorage.setItem('rv_user', username);
  }

  logout() {
    localStorage.removeItem('rv_token');
    localStorage.removeItem('rv_role');
    localStorage.removeItem('rv_user');
  }

  getCurrentUser() {
    return {
      token: this.getToken(),
      role: localStorage.getItem('rv_role') || 'VIEWER',
      username: localStorage.getItem('rv_user') || 'Guest'
    };
  }

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = {
      ...options.headers
    };

    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    if (res.status === 401) {
      this.logout();
    }

    if (!res.ok) {
      let errDetail = 'API request failed';
      try {
        const errJson = await res.json();
        errDetail = errJson.detail || errDetail;
      } catch (e) {
        errDetail = res.statusText || errDetail;
      }
      throw new Error(errDetail);
    }

    return res.json();
  }

  // Auth
  async login(username, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setToken(data.access_token, data.role, data.username);
    return data;
  }

  // Cameras
  async getCameras() {
    return this.request('/api/cameras');
  }

  async getCamera(id) {
    return this.request(`/api/cameras/${id}`);
  }

  async testCamera(id) {
    return this.request(`/api/cameras/${id}/test`, { method: 'POST' });
  }

  async createCamera(data) {
    return this.request('/api/cameras', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async updateCamera(id, data) {
    return this.request(`/api/cameras/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  async deleteCamera(id) {
    return this.request(`/api/cameras/${id}`, { method: 'DELETE' });
  }

  async getResortMapGraph() {
    return this.request('/api/cameras/map/graph');
  }

  getCameraStreamUrl(id) {
    return `${API_BASE_URL}/api/cameras/${id}/stream`;
  }

  getCameraSnapshotUrl(id) {
    return `${API_BASE_URL}/api/cameras/${id}/snapshot`;
  }

  // Persons
  async getPersons() {
    return this.request('/api/persons');
  }

  async getPerson(id) {
    return this.request(`/api/persons/${id}`);
  }

  async getPersonTimeline(id) {
    return this.request(`/api/persons/${id}/timeline`);
  }

  async registerPerson(formData) {
    return this.request('/api/persons/register', {
      method: 'POST',
      body: formData
    });
  }

  async deletePerson(id) {
    return this.request(`/api/persons/${id}`, { method: 'DELETE' });
  }

  // Search
  async searchStructured(query) {
    return this.request('/api/search/structured', {
      method: 'POST',
      body: JSON.stringify(query)
    });
  }

  async searchNlp(query) {
    return this.request('/api/search/nlp', {
      method: 'POST',
      body: JSON.stringify({ query })
    });
  }

  // Alerts
  async getAlerts(status) {
    const qs = status ? `?status=${status}` : '';
    return this.request(`/api/alerts${qs}`);
  }

  async updateAlertStatus(id, newStatus) {
    return this.request(`/api/alerts/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status: newStatus })
    });
  }

  // Analytics & Predictions
  async getDashboardAnalytics() {
    return this.request('/api/analytics/dashboard');
  }

  async getChartsAnalytics() {
    return this.request('/api/analytics/charts');
  }

  async getPrediction(personId) {
    return this.request(`/api/predictions/${personId}`);
  }

  // Experiments
  async getExperimentResults() {
    return this.request('/api/experiments/results');
  }

  async runExperimentBenchmark(numSamples) {
    return this.request('/api/experiments/run', {
      method: 'POST',
      body: JSON.stringify({ num_test_sequences: numSamples })
    });
  }

  async getFusionWeights() {
    return this.request('/api/experiments/weights');
  }

  async updateFusionWeights(weights) {
    return this.request('/api/experiments/weights', {
      method: 'POST',
      body: JSON.stringify(weights)
    });
  }
}

export const api = new ApiService();
