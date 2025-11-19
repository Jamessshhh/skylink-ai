# src/logic.py
import networkx as nx
from math import radians, cos, sin, asin, sqrt
import pandas as pd

def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two points on Earth."""
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # Radius of earth in km
    return c * r

def build_graph(routes, airports, airlines):
    G = nx.Graph()
    
    # Clean Data - Ensure unique IATA codes for lookup
    valid_airports = airports.dropna(subset=["IATA"]).drop_duplicates(subset=["IATA"])
    airport_dict = valid_airports.set_index("IATA")[["Latitude", "Longitude", "City", "Name"]].to_dict('index')

    valid_airlines = airlines.dropna(subset=["IATA"]).drop_duplicates(subset=["IATA"])
    airline_dict = valid_airlines.set_index("IATA")["Name"].to_dict()

    # Filter routes to only include valid airports
    valid_routes = routes[
        (routes["SourceAirport"].isin(airport_dict)) & 
        (routes["DestAirport"].isin(airport_dict))
    ]

    for _, row in valid_routes.iterrows():
        src, dest, airline = row["SourceAirport"], row["DestAirport"], row["Airline"]
        
        # Only add edges if both source and dest exist in our valid airport list
        if src in airport_dict and dest in airport_dict:
            src_lat, src_lon = airport_dict[src]["Latitude"], airport_dict[src]["Longitude"]
            dest_lat, dest_lon = airport_dict[dest]["Latitude"], airport_dict[dest]["Longitude"]
            
            dist = haversine(src_lon, src_lat, dest_lon, dest_lat)
            airline_name = airline_dict.get(airline, airline)
            
            # Add edge
            G.add_edge(src, dest, weight=dist, airline=airline_name, distance=dist)
            
            # Add node attributes
            nx.set_node_attributes(G, {src: airport_dict[src], dest: airport_dict[dest]})
            
    return G

def find_shortest_path(G, src, dest):
    # --- CRITICAL FIX: Check if nodes exist before searching ---
    if src not in G:
        return None, 0 # Source airport not in the selected airline network
    if dest not in G:
        return None, 0 # Destination airport not in the selected airline network
    # ----------------------------------------------------------

    try:
        path = nx.shortest_path(G, src, dest, weight="weight")
        details = []
        total_dist = 0
        
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            edge_data = G.get_edge_data(u, v)
            dist = edge_data['distance']
            total_dist += dist
            details.append({
                "from": u, "to": v,
                "airline": edge_data['airline'],
                "distance": dist,
                "coords_u": (G.nodes[u]['Latitude'], G.nodes[u]['Longitude']),
                "coords_v": (G.nodes[v]['Latitude'], G.nodes[v]['Longitude'])
            })
            
        return details, total_dist
    except nx.NetworkXNoPath:
        return None, 0
    

    # src/logic.py (Add this to the bottom)

def calculate_emissions(distance_km):
    """
    Calculates CO2 emissions (kg) based on distance.
    Avg: ~0.115 kg CO2 per passenger per km.
    """
    return round(distance_km * 0.115, 2)