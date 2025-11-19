# app.py
import streamlit as st
import folium
from streamlit_folium import st_folium
from src.utils import load_data, parse_natural_language_query
from src.logic import build_graph, find_shortest_path, calculate_emissions
from src.ml_engine import predict_delay, predict_price
from src.ai_chat import get_travel_advice

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SkyLink AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed sidebar to focus on main content
)

# --- 2. CUSTOM CSS (CYBERPUNK / GLASS) ---
st.markdown("""
    <style>
        /* Main Background */
        .stApp {
            background: #0e1117;
        }
        
        /* Gradient Title */
        .title-text {
            font-weight: 700;
            font-size: 40px !important;
            background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px;
            text-align: center;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
        }
        .metric-label {
            font-size: 12px;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Chat Message Styling */
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px 5px 0px 0px;
            color: white;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1f7a57 !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "path_details" not in st.session_state: st.session_state.path_details = None
if "total_dist" not in st.session_state: st.session_state.total_dist = 0
if "nlp_origin" not in st.session_state: st.session_state.nlp_origin = None
if "nlp_dest" not in st.session_state: st.session_state.nlp_dest = None
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. DATA LOADING ---
with st.spinner("🚀 Booting SkyLink Systems..."):
    airports, airlines, routes = load_data()
    airport_options = dict(zip(airports["Label"], airports["IATA"]))

# --- 5. TOP NAVIGATION (SEARCH) ---
col_logo, col_search = st.columns([1, 3])
with col_logo:
    st.markdown('<h1 class="title-text">SkyLink AI</h1>', unsafe_allow_html=True)

with col_search:
    nlp_query = st.text_input("🧠  Search", placeholder="Type naturally: 'Fly from Tokyo to Sydney'...")
    if nlp_query:
        found_origin, found_dest = parse_natural_language_query(nlp_query, airport_options)
        if found_origin and found_dest:
            st.session_state.nlp_origin = found_origin
            st.session_state.nlp_dest = found_dest

# Expandable Manual Controls
with st.expander("⚙️ Manual Selection & Filters"):
    c1, c2 = st.columns(2)
    with c1:
        origin_label = st.selectbox("📍 Origin", options=airport_options.keys(), 
                                    index=list(airport_options.keys()).index(st.session_state.nlp_origin) if st.session_state.nlp_origin else None)
    with c2:
        dest_label = st.selectbox("🏁 Destination", options=airport_options.keys(), 
                                  index=list(airport_options.keys()).index(st.session_state.nlp_dest) if st.session_state.nlp_dest else None)
    
    # Airline Filter
    preferred_airlines = st.multiselect("Filter Airlines", options=airlines["Name"].sort_values().unique())
    
    if preferred_airlines:
        selected_iata = airlines[airlines["Name"].isin(preferred_airlines)]["IATA"].tolist()
        active_routes = routes[routes["Airline"].isin(selected_iata)]
    else:
        active_routes = routes

    # Refresh Button
    if st.button("🔄 Refresh Network Graph"):
        G = build_graph(active_routes, airports, airlines)
        st.session_state.G = G
        st.success("Network Updated.")
    
    if "G" not in st.session_state:
        G = build_graph(active_routes, airports, airlines)
        st.session_state.G = G
    else:
        G = st.session_state.G

# --- 6. ACTION & RESULTS ---
if st.button("🚀 Launch Route Analysis", type="primary", use_container_width=True):
    if origin_label and dest_label:
        origin_code, dest_code = airport_options[origin_label], airport_options[dest_label]
        
        with st.spinner("🛰️ Triangulating optimal path..."):
            path, dist = find_shortest_path(G, origin_code, dest_code)
            st.session_state.path_details = path
            st.session_state.total_dist = dist
            st.session_state.chat_history = [] # Reset chat on new search

# --- 7. MAIN TABS (THE NEW UI) ---
if st.session_state.path_details:
    path = st.session_state.path_details
    
    # Calculate Metrics
    total_price = 0
    for leg in path:
        duration = int((leg['distance'] / 800) * 60 + 45)
        total_price += predict_price(duration, 0, leg['airline'])
    total_emissions = calculate_emissions(st.session_state.total_dist)

    # Metrics Bar (Always Visible)
    m1, m2, m3 = st.columns(3)
    with m1: st.markdown(f"<div class='glass-card'><div class='metric-label'>Total Distance</div><div class='metric-value'>{int(st.session_state.total_dist):,} km</div></div>", unsafe_allow_html=True)
    with m2: st.markdown(f"<div class='glass-card'><div class='metric-label'>Estimated Cost</div><div class='metric-value'>${int(total_price):,}</div></div>", unsafe_allow_html=True)
    with m3: st.markdown(f"<div class='glass-card'><div class='metric-label'>Carbon Footprint</div><div class='metric-value'>{int(total_emissions)} kg</div></div>", unsafe_allow_html=True)

    # TABS
    tab_map, tab_chat = st.tabs(["🗺️ Route Visualization", "🤖 AI Companion"])

    # --- TAB 1: MAP & LOGISTICS ---
    with tab_map:
        c_map, c_list = st.columns([2, 1])
        
        with c_map:
            start_coords = path[0]['coords_u']
            m = folium.Map(location=start_coords, zoom_start=3, tiles="CartoDB dark_matter")
            for leg in path:
                folium.PolyLine([leg['coords_u'], leg['coords_v']], color="#00C9FF", weight=4, opacity=0.8).add_to(m)
                folium.Marker(leg['coords_u'], popup=leg['from'], icon=folium.Icon(color="blue", icon="plane", prefix="fa")).add_to(m)
            folium.Marker(path[-1]['coords_v'], popup="DEST", icon=folium.Icon(color="red", icon="flag", prefix="fa")).add_to(m)
            st_folium(m, height=500, use_container_width=True)
            
        with c_list:
            st.markdown("#### 🎫 Itinerary")
            for i, leg in enumerate(path):
                duration = int((leg['distance'] / 800) * 60 + 45)
                price = predict_price(duration, 0, leg['airline'])
                risk = predict_delay(leg['distance'], "rain", leg['airline'])
                risk_color = "#ff4444" if risk > 0.5 else "#00C9FF"
                
                with st.container(border=True):
                    st.markdown(f"**Leg {i+1}: {leg['from']} ➝ {leg['to']}**")
                    st.caption(f"{leg['airline']}")
                    st.markdown(f"Delay Risk: <span style='color:{risk_color}'>{risk:.0%}</span>", unsafe_allow_html=True)

    # --- TAB 2: AI TRAVEL COMPANION (CENTRALIZED) ---
    with tab_chat:
        st.markdown("### 💬 Ask your AI Guide")
        
        # Determine Destination Name for Context
        dest_name = dest_label.split(" - ")[0] if dest_label else "your destination"
        
        # Get Key
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
        else:
            api_key = st.text_input("Enter Groq API Key for live answers:", type="password")

        # Quick Action Buttons
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        prompt = None
        if col_q1.button("🍽️ Food Guide"): prompt = f"What is the best local food to eat in {dest_name}?"
        if col_q2.button("⚠️ Safety Tips"): prompt = f"Is {dest_name} safe for tourists? Any warnings?"
        if col_q3.button("🎒 Packing List"): prompt = f"What should I pack for a trip to {dest_name}?"
        if col_q4.button("🏛️ Must Visit"): prompt = f"What are the top 3 hidden gems in {dest_name}?"

        # Handle User Input (Manual or Button)
        user_input = st.chat_input(f"Ask about {dest_name}...")
        
        if prompt: user_input = prompt # Override if button clicked

        # Process Chat
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 AI is thinking..."):
                ai_reply = get_travel_advice(dest_name, user_input, api_key)
            
            st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})

        # Render Chat History (Like WhatsApp/iMessage)
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])