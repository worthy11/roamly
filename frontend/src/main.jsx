import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {createBrowserRouter, RouterProvider} from "react-router-dom"
import './index.css'
import App from './App.jsx'
import Travel from './pages/Travels.jsx'
import ErrorPage from './pages/ErrorPage.jsx'
import Chat from './pages/Chat.jsx'
import Login from './Login.jsx'

const router = createBrowserRouter([
  {path: "/", element: <Login />},
  {path: "/app", element: <App />},
  {path: "/travels", element: <Travel />},
  {path: "*", element: <ErrorPage />},
  {path: "/chat", element: <Chat /> }
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router}/>
  </StrictMode>,
)
