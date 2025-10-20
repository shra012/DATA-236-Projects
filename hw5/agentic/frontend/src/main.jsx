import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { Provider } from "react-redux";
import App from "./App.jsx";
import "./styles.css";
import { store } from "./state";

createRoot(document.getElementById('root')).render(
  <Provider store={store}>
    <App />
  </Provider>
);
