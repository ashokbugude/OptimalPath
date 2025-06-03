# Route Optimization

Python-based route optimization tool that finds the most efficient path between cities in India using both road and railway networks. The application uses Google OR-Tools for optimization and Folium for interactive map visualization.
![image](https://github.com/user-attachments/assets/12f747d3-2758-482b-9a0b-ddb9d5888cdd)

## Features

- **Multi-Modal Transportation**: Optimizes routes using both road and railway networks
- **Interactive Map Visualization**: Displays routes with detailed information on an interactive map
- **Optimal Route Finding**: Uses Google OR-Tools to find the most efficient path
- **Detailed Statistics**: Shows comprehensive route statistics including:
  - Total distance
  - Road and railway segments
  - Number of cities visited
  - Complete route sequence

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TigerFreight.git
   cd TigerFreight
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
TigerFreight/
├── data/
│   ├── city_coordinates.csv    # City coordinates data
│   ├── road_distances_india.csv    # Road distances between cities
│   └── railway_distances_india.csv # Railway distances between cities
├── output/
│   └── route_map.html         # Generated map visualization
├── tsp_solver.py              # Main optimization algorithm
├── predict_route.py           # Application entry point
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Data Files

### city_coordinates.csv
Contains latitude and longitude coordinates for each city:
- City: City name
- Latitude: City's latitude
- Longitude: City's longitude

### road_distances_india.csv
Contains road distances between cities:
- From: Starting city
- To: Destination city
- Distance: Distance in kilometers

### railway_distances_india.csv
Contains railway distances between cities:
- From: Starting city
- To: Destination city
- Distance: Distance in kilometers

## Usage

1. Run the application:
   ```bash
   python predict_route.py
   ```

2. Enter the starting city when prompted (default: Delhi)

3. Enter the destination city when prompted (default: Kolkata)

4. The application will:
   - Find the optimal route
   - Display route details in the console
   - Generate an interactive map visualization
   - Open the map in your default web browser

## Map Features

The generated map includes:

1. **Location Markers**:
   - Blue marker: Starting city
   - Red markers: Intermediate cities
   - Green marker: Destination city
   - Information icon (i) on each marker

2. **Route Lines**:
   - Blue lines: Road segments
   - Red lines: Railway segments
   - Hover tooltips showing distance and mode

3. **Information Panels**:
   - Route Statistics (bottom left)
   - Legend (bottom right)
   - Click markers for detailed segment information

4. **Interactive Features**:
   - Zoom in/out
   - Pan the map
   - Fullscreen mode
   - Layer control

## Technical Details

### Optimization Algorithm
- Uses Google OR-Tools for route optimization
- Implements a constraint solver for finding optimal paths
- Considers both road and railway distances
- Optimizes for minimum total distance

### Map Visualization
- Built using Folium (Python wrapper for Leaflet.js)
- Interactive markers with custom icons
- Color-coded route segments
- Detailed popups with segment information
- Responsive design with fixed information panels

### Data Processing
- Efficient distance matrix computation
- Best mode selection between cities
- Symmetric distance handling
- Error handling for missing data

## Dependencies

- numpy: Numerical computations
- pandas: Data manipulation
- folium: Map visualization
- ortools: Route optimization
- webbrowser: Browser integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google OR-Tools for optimization algorithms
- Folium for map visualization
- OpenStreetMap for map data 
