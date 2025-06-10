import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Placeholder components
const Dashboard = () => (
  <div className="p-8">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">Google Search API Dashboard</h1>
    <p className="text-gray-600">Welcome to your search analytics dashboard.</p>
  </div>
);

const Login = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="max-w-md w-full space-y-8">
      <div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Sign in to your account
        </h2>
      </div>
      <div className="bg-white p-8 rounded-lg shadow">
        <p className="text-center text-gray-600">Login functionality to be implemented</p>
      </div>
    </div>
  </div>
);

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={user ? <Dashboard /> : <Login />} />
      </Routes>
    </div>
  );
}

export default App;