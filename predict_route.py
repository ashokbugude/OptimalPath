from tsp_solver import TSPSolver
import os

def find_optimal_route(start_city='Delhi', end_city='Kolkata'):
    print("Loading data and finding optimal route...")
    
    # Create TSP solver instance
    solver = TSPSolver()
    
    # Print available cities
    print("\nAvailable cities:")
    print(", ".join(sorted(solver.cities.keys())))
    
    # Validate cities
    if start_city not in solver.cities:
        print(f"Error: Starting city '{start_city}' not found in available cities.")
        return
    
    if end_city not in solver.cities:
        print(f"Error: Destination city '{end_city}' not found in available cities.")
        return
    
    if start_city == end_city:
        print("Error: Starting and destination cities cannot be the same.")
        return
    
    # Get optimal route using OR-Tools
    print(f"\nFinding optimal route from {start_city} to {end_city}...")
    route = solver.solve_tsp_optimal(start_city, end_city)
    
    if not route:
        print("No route found.")
        return
    
    # Print route details
    solver.print_route_details(route)
    
    # Plot the route on map
    print("\nGenerating interactive map visualization...")
    solver.plot_route_on_map(route)

if __name__ == "__main__":
    # Get user input for cities
    print("Enter the starting city (default: Delhi):")
    start_city = input().strip() or 'Delhi'
    
    print("Enter the destination city (default: Kolkata):")
    end_city = input().strip() or 'Kolkata'
    
    find_optimal_route(start_city, end_city) 