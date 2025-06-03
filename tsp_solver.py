import numpy as np
import pandas as pd
import folium
from folium import plugins
import webbrowser
import os
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class TSPSolver:
    def __init__(self):
        self.cities = {}
        self.distance_matrices = {'road': None, 'railway': None}
        self.city_coords = {}
        self.best_mode_matrix = None  # Matrix to store best mode between cities
        self.best_distance_matrix = None  # Matrix to store best distances
        self.load_city_coordinates()
        self.load_distance_matrices()
        
    def load_city_coordinates(self):
        """Load city coordinates from CSV file."""
        try:
            coords_df = pd.read_csv('data/city_coordinates.csv')
            for _, row in coords_df.iterrows():
                self.city_coords[row['City']] = (row['Latitude'], row['Longitude'])
                self.add_city(row['City'], row['Latitude'], row['Longitude'])
            print(f"Loaded coordinates for {len(self.city_coords)} cities")
        except Exception as e:
            print(f"Error loading city coordinates: {str(e)}")
        
    def load_distance_matrices(self):
        """Load road and railway distance matrices from CSV files as edge lists and build lookup dictionaries."""
        try:
            # Load as edge lists
            road_df = pd.read_csv('data/road_distances_india.csv')
            rail_df = pd.read_csv('data/railway_distances_india.csv')
            
            # Build lookup dictionaries
            self.road_lookup = {}
            self.rail_lookup = {}
            for _, row in road_df.iterrows():
                self.road_lookup[(row['From'], row['To'])] = row['Distance']
                self.road_lookup[(row['To'], row['From'])] = row['Distance']
            for _, row in rail_df.iterrows():
                self.rail_lookup[(row['From'], row['To'])] = row['Distance']
                self.rail_lookup[(row['To'], row['From'])] = row['Distance']
            
            # Ensure cities dictionary is populated
            for city in set(road_df['From']).union(set(road_df['To'])):
                if city not in self.cities:
                    self.add_city(city)
            print(f"Loaded distance edge lists for {len(self.cities)} cities")
            self.compute_best_mode_matrix()
        except Exception as e:
            print(f"Error loading distance matrices: {str(e)}")
        
    def add_city(self, name, lat=None, lon=None):
        """Add a city to the solver."""
        if name not in self.cities:
            self.cities[name] = len(self.cities)
            if lat is not None and lon is not None:
                self.city_coords[name] = (lat, lon)
            
    def set_distance(self, city1, city2, distance, mode='road'):
        """Set the distance between two cities."""
        if mode not in self.distance_matrices:
            self.distance_matrices[mode] = None
        if self.distance_matrices[mode] is None:
            n = len(self.cities)
            self.distance_matrices[mode] = np.zeros((n, n))
            
        idx1 = self.cities[city1]
        idx2 = self.cities[city2]
        self.distance_matrices[mode][idx1][idx2] = distance
        self.distance_matrices[mode][idx2][idx1] = distance  # Distance is symmetric
        
    def compute_best_mode_matrix(self):
        """Compute the best mode (road/rail) between each pair of cities using lookups."""
        n = len(self.cities)
        self.best_mode_matrix = np.full((n, n), 'none', dtype=object)
        self.best_distance_matrix = np.full((n, n), np.inf)
        city_names = list(self.cities.keys())
        for i, city1 in enumerate(city_names):
            for j, city2 in enumerate(city_names):
                if i != j:
                    road_dist = self.road_lookup.get((city1, city2), np.inf)
                    rail_dist = self.rail_lookup.get((city1, city2), np.inf)
                    if np.isfinite(road_dist) and np.isfinite(rail_dist):
                        if road_dist <= rail_dist:
                            self.best_mode_matrix[i][j] = 'road'
                            self.best_distance_matrix[i][j] = road_dist
                        else:
                            self.best_mode_matrix[i][j] = 'railway'
                            self.best_distance_matrix[i][j] = rail_dist
                    elif np.isfinite(road_dist):
                        self.best_mode_matrix[i][j] = 'road'
                        self.best_distance_matrix[i][j] = road_dist
                    elif np.isfinite(rail_dist):
                        self.best_mode_matrix[i][j] = 'railway'
                        self.best_distance_matrix[i][j] = rail_dist
                    else:
                        self.best_mode_matrix[i][j] = 'none'
                        self.best_distance_matrix[i][j] = np.inf

    def solve_tsp_optimal(self, start_city, end_city=None):
        """Solve the TSP optimally using OR-Tools, visiting all cities from start_city to end_city."""
        if self.best_distance_matrix is None:
            self.compute_best_mode_matrix()
        n = len(self.cities)
        city_names = list(self.cities.keys())
        start_idx = self.cities[start_city]
        if end_city:
            end_idx = self.cities[end_city]
        else:
            end_idx = start_idx
        matrix = self.best_distance_matrix
        int_matrix = [[int(x) if np.isfinite(x) else 999999 for x in row] for row in matrix]
        manager = pywrapcp.RoutingIndexManager(
            n, 1, [start_idx], [end_idx]
        )
        routing = pywrapcp.RoutingModel(manager)
        def distance_callback(from_index, to_index):
            return int_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
        search_parameters.time_limit.seconds = 30
        solution = routing.SolveWithParameters(search_parameters)
        if not solution:
            print("No solution found by OR-Tools.")
            return None
        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(city_names[manager.IndexToNode(index)])
            index = solution.Value(routing.NextVar(index))
        route.append(city_names[manager.IndexToNode(index)])
        return route

    def print_route_details(self, route):
        """Print detailed information about the route."""
        if self.best_distance_matrix is None:
            self.compute_best_mode_matrix()
            
        total_distance = 0
        print("\nOptimal Route Details (Best Mode Selected):")
        print("-" * 70)
        
        # Print route segments
        for i in range(len(route)-1):
            city1 = route[i]
            city2 = route[i+1]
            idx1 = self.cities[city1]
            idx2 = self.cities[city2]
            mode = self.best_mode_matrix[idx1][idx2]
            distance = self.best_distance_matrix[idx1][idx2]
            total_distance += distance
            print(f"{city1} → {city2}: {distance:.1f} km ({mode})")
        
        print("-" * 70)
        print(f"Total Distance: {total_distance:.1f} km")
        print(f"Number of Cities Visited: {len(route)}")
        print(f"Cities in Route: {' → '.join(route)}")

    def plot_route_on_map(self, route):
        """Plot the route on an interactive map with detailed information."""
        if not self.city_coords:
            print("Error: City coordinates not available.")
            return
            
        # Create a map centered on India
        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        # Calculate route statistics
        total_distance = 0
        road_distance = 0
        railway_distance = 0
        road_segments = 0
        railway_segments = 0
        
        # Create a feature group for the route
        route_group = folium.FeatureGroup(name='Route')
        
        # Add markers and lines for each city in the route
        for i in range(len(route)-1):
            city1 = route[i]
            city2 = route[i+1]
            
            # Get coordinates
            if city1 in self.city_coords and city2 in self.city_coords:
                lat1, lon1 = self.city_coords[city1]
                lat2, lon2 = self.city_coords[city2]
                
                # Get mode and distance
                idx1 = self.cities[city1]
                idx2 = self.cities[city2]
                mode = self.best_mode_matrix[idx1][idx2]
                distance = self.best_distance_matrix[idx1][idx2]
                
                # Update statistics
                total_distance += distance if np.isfinite(distance) else 0
                if mode == 'road':
                    road_distance += distance if np.isfinite(distance) else 0
                    road_segments += 1
                elif mode == 'railway':
                    railway_distance += distance if np.isfinite(distance) else 0
                    railway_segments += 1
                
                # Create popup content with detailed information
                mode_str = mode.title() if isinstance(mode, str) and mode not in ['none', ''] else 'N/A'
                popup_content = f"""
                <div style='width: 200px'>
                    <h4 style='margin-bottom: 5px'>{city1} → {city2}</h4>
                    <p style='margin: 2px 0'><b>Distance:</b> {distance:.1f} km</p>
                    <p style='margin: 2px 0'><b>Mode:</b> {mode_str}</p>
                    <p style='margin: 2px 0'><b>Segment:</b> {i+1} of {len(route)-1}</p>
                </div>
                """
                
                # Add markers with custom icons
                if i == 0:
                    icon_color = 'blue'  # Start city
                else:
                    icon_color = 'red'   # Intermediate cities
                folium.Marker(
                    [lat1, lon1],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=icon_color, icon='info-circle', prefix='fa'),
                    tooltip=f"{city1} → {city2}"
                ).add_to(route_group)
                
                # Add lines with different colors for different modes
                color = 'blue' if mode == 'road' else 'red' if mode == 'railway' else 'gray'
                folium.PolyLine(
                    locations=[[lat1, lon1], [lat2, lon2]],
                    color=color,
                    weight=3,
                    opacity=0.8,
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{distance:.1f} km ({mode_str})"
                ).add_to(route_group)
        
        # Add the last city marker
        if route[-1] in self.city_coords:
            lat, lon = self.city_coords[route[-1]]
            folium.Marker(
                [lat, lon],
                popup=f"<b>Final Destination:</b> {route[-1]}",
                icon=folium.Icon(color='green', icon='info-circle', prefix='fa'),
                tooltip=f"Destination: {route[-1]}"
            ).add_to(route_group)
        
        # Add the route group to the map
        route_group.add_to(m)
        
        # Add route statistics to the map
        stats_html = f'''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; 
             padding: 15px; border: 2px solid grey; border-radius: 5px; width: 300px;">
            <h4 style="margin-top: 0">Route Statistics</h4>
            <p style="margin: 5px 0"><b>Total Distance:</b> {total_distance:.1f} km</p>
            <p style="margin: 5px 0"><b>Road Distance:</b> {road_distance:.1f} km ({road_segments} segments)</p>
            <p style="margin: 5px 0"><b>Railway Distance:</b> {railway_distance:.1f} km ({railway_segments} segments)</p>
            <p style="margin: 5px 0"><b>Total Cities:</b> {len(route)}</p>
            <p style="margin: 5px 0"><b>Route:</b> {' → '.join(route)}</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(stats_html))
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; background-color: white; 
             padding: 15px; border: 2px solid grey; border-radius: 5px;">
            <h4 style="margin-top: 0">Legend</h4>
            <p style="margin: 5px 0"><span style="color: blue;">●</span> Road Transport</p>
            <p style="margin: 5px 0"><span style="color: red;">●</span> Railway Transport</p>
            <p style="margin: 5px 0"><span style="color: blue;">●</span> Starting City</p>
            <p style="margin: 5px 0"><span style="color: red;">●</span> Intermediate Cities</p>
            <p style="margin: 5px 0"><span style="color: green;">●</span> Destination City</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(m)
        
        # Save the map in the 'output' folder
        os.makedirs('output', exist_ok=True)
        map_file = os.path.join('output', 'route_map.html')
        m.save(map_file)
        
        # Open the map in the default web browser
        webbrowser.open('file://' + os.path.realpath(map_file)) 