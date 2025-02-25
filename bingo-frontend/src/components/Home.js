import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const API_URL = process.env.REACT_APP_API_URL;

const Home = () => {
  const [tasks, setTasks] = useState([]);  // ✅ Correctly define state
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        setTasks(response.data);  // ✅ Properly update tasks
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    };

    fetchTasks();
  }, [setTasks]);  
  // ✅ Include setTasks in dependencies to satisfy ESLint

  return (
    <div className="home-container">
      <h1>Bingo Game Board</h1>
      <p>Complete tasks to earn points and win!</p>

      <div className="buttons">
        <button onClick={() => navigate('/leaderboard')}>View Leaderboard</button>
        <button onClick={() => navigate('/login')}>Login</button>
      </div>
    </div>
  );
};

export default Home;
