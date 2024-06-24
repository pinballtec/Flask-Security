import React, { useState } from 'react';
import api from '../api';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await api.post('/signin', { email, password });
      alert(response.data.message);
    } catch (error) {
      if (error.response) {
        // Сервер ответил с кодом статуса, который не входит в диапазон 2xx
        alert('Login failed: ' + error.response.data.message);
      } else if (error.request) {
        // Запрос был сделан, но ответа не было
        alert('No response from server. Please try again later.');
      } else {
        // Произошла ошибка при настройке запроса
        alert('Error: ' + error.message);
      }
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

export default Login;
