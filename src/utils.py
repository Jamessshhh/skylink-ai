# src/utils.py
import pandas as pd
import streamlit as st
import re

@st.cache_data
def load_data():
    """
    Loads and joins the Airports, Airlines, and Routes databases.
    Includes smart sorting so popular airports appear first.
    """
    # 1. Load Routes FIRST (to calculate popularity)
    cols_routes = ["Airline", "AirlineID", "SourceAirport", "SourceAirportID", "DestAirport", "DestAirportID", "Codeshare", "Stops", "Equipment"]
    routes = pd.read_csv("data/routes.dat", header=None, names=cols_routes, na_values=["\\N"])
    routes = routes.dropna(subset=["SourceAirport", "DestAirport"])

    # Calculate Airport Popularity (Number of routes)
    route_counts = routes["SourceAirport"].value_counts().add(routes["DestAirport"].value_counts(), fill_value=0)

    # 2. Load Airports
    cols_airports = ["AirportID", "Name", "City", "Country", "IATA", "ICAO", "Latitude", "Longitude", "Altitude", "Timezone", "DST", "Tz", "Type", "Source"]
    airports = pd.read_csv("data/airports.dat", header=None, names=cols_airports, na_values=["\\N"])
    
    # Filter out invalid rows
    airports = airports.dropna(subset=["IATA", "City", "Name"])
    
    # Map popularity score to airports
    airports["RouteCount"] = airports["IATA"].map(route_counts).fillna(0)
    
    # Sort by RouteCount (Descending), so big airports come first
    airports = airports.sort_values(by="RouteCount", ascending=False)

    # Create the Label for dropdowns
    airports["Label"] = (
        airports["City"] + ", " + 
        airports["Country"] + " (" + 
        airports["IATA"] + ") - " + 
        airports["Name"]
    )

    # 3. Load Airlines
    cols_airlines = ["AirlineID", "Name", "Alias", "IATA", "ICAO", "Callsign", "Country", "Active"]
    airlines = pd.read_csv("data/airlines.dat", header=None, names=cols_airlines, na_values=["\\N"])
    airlines = airlines[airlines["Active"] == "Y"]

    return airports, airlines, routes

def parse_natural_language_query(query, airport_options):
    """
    Extracts Origin and Destination from sentences like:
    'Fly from Mumbai to Paris' or 'New York to Tokyo'
    """
    if not query: return None, None
    
    query = query.lower()
    
    # Logic 1: Look for 'from X to Y' pattern
    match = re.search(r"from\s+(.+?)\s+to\s+(.+)", query)
    
    origin_name, dest_name = None, None
    
    if match:
        origin_name = match.group(1).strip()
        dest_name = match.group(2).strip()
    elif " to " in query:
        parts = query.split(" to ")
        origin_name = parts[0].strip()
        dest_name = parts[1].strip()
    else:
        return None, None # Failed to parse

    # Attempt to match names to our airport list
    # We do a loose search in the "Label" keys
    found_origin = None
    found_dest = None
    
    # Helper to find best match (first partial match in our sorted list)
    for label in airport_options.keys():
        if origin_name and not found_origin and origin_name in label.lower():
            found_origin = label
        if dest_name and not found_dest and dest_name in label.lower():
            found_dest = label
            
        if found_origin and found_dest:
            break
            
    return found_origin, found_dest