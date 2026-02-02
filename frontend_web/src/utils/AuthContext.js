import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('chemviz_token');
    const username = localStorage.getItem('chemviz_username');
    if (token && username) {
      setUser({ username, token });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const res = await apiLogin(username, password);
    const { token, username: uname } = res.data;
    localStorage.setItem('chemviz_token', token);
    localStorage.setItem('chemviz_username', uname);
    setUser({ username: uname, token });
    return res.data;
  };

  const register = async (username, email, password) => {
    const res = await apiRegister(username, email, password);
    const { token, username: uname } = res.data;
    localStorage.setItem('chemviz_token', token);
    localStorage.setItem('chemviz_username', uname);
    setUser({ username: uname, token });
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('chemviz_token');
    localStorage.removeItem('chemviz_username');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
