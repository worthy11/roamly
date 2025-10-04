import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import App from "./App.jsx";
import Travel from "./pages/Travels.jsx";
import ErrorPage from "./pages/ErrorPage.jsx";
import Login from "./Login.jsx";

const router = createBrowserRouter([
  { path: "/", element: <App /> },
  { path: "/travels", element: <Travel /> },
  { path: "*", element: <ErrorPage /> },
]);

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
