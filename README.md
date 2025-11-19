# 🌍 SkyLink AI: Intelligent Flight Route Optimizer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://skylink-ai.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![AI](https://img.shields.io/badge/AI-Llama%203-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**SkyLink AI** is a full-stack travel technology platform that combines **Graph Theory**, **Machine Learning**, and **Generative AI** to solve complex flight routing problems. Unlike standard search engines, it visualizes the underlying graph network, estimates costs using regression models, and provides an AI travel consultant for destination advice.

🔗 **[Live Demo]([https://skylink-ai.streamlit.app](https://skylink-ai-mlig9fjrd4tx5jihgaceb8.streamlit.app))**

---

## 🚀 Key Features

### 🧠 1. Intelligent Pathfinding
- Uses **Dijkstra’s Algorithm** (via `NetworkX`) to calculate the mathematically optimal route between thousands of global airports.
- Visualizes the flight path interactively on a global map using **Folium**.

### 🔮 2. ML Price Prediction
- Features a custom **Random Forest Regressor** trained on historical flight data (Kaggle dataset).
- Predicts ticket prices based on flight duration, airline category, and stopovers.
- **Tech:** `Scikit-Learn`, `Joblib`, `Pandas`.

### 🤖 3. Generative AI Travel Assistant
- Integrated **Llama 3.1** (via Groq API) to act as a real-time travel guide.
- Users can ask context-aware questions (e.g., *"What is the best food in Mumbai?"*) and receive instant, localized advice.

### 🗣️ 4. NLP Smart Search
- Includes a Natural Language Processing parser.
- Users can type commands like *"Fly from New York to London"* instead of using dropdown menus.

### 🌱 5. Sustainability Tracking
- Automatically calculates the **Carbon Footprint** (kg CO₂) for every itinerary.
- Assigns "Eco-Friendly" badges to efficient routes to encourage sustainable travel.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Cyberpunk-themed UI with Glassmorphism elements |
| **Backend Logic** | Python | Core application logic |
| **Graph Network** | NetworkX | Building and traversing the airport node graph |
| **Machine Learning** | Scikit-Learn | Random Forest models for Price & Delay prediction |
| **LLM / GenAI** | Groq API (Llama 3) | Generative text for the travel assistant |
| **Visualization** | Folium / Leaflet | Interactive geospatial mapping |
| **Data Processing** | Pandas | ETL pipelines for OpenFlights & Kaggle datasets |

---

## 📂 Project Structure

```text
AI-FLIGHT-ROUTE-OPTIMIZATION/
├── .streamlit/          # Secrets management (API Keys)
├── data/                # Airlines, Airports, and Routes datasets (.dat/.csv)
├── models/              # Serialized ML models (.pkl)
├── src/                 # Source Code
│   ├── ai_chat.py       # Groq/Llama 3 integration logic
│   ├── logic.py         # Graph theory & Haversine calculations
│   ├── ml_engine.py     # ML Training & Inference pipelines
│   └── utils.py         # Data loading, cleaning & NLP parsing
├── app.py               # Main Streamlit Application Entry Point
└── requirements.txt     # Project Dependencies

