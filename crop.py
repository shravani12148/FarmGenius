import folium
import random
from folium import LayerControl
from branca.element import Template, MacroElement

# Maharashtra center coordinates
center_coords = [19.75, 75.71]
zoom_level = 7

# Maharashtra boundary (simplified)
maharashtra_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"name": "Maharashtra"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [72.6, 18.8], [73.2, 15.7], [75.3, 15.8], [76.8, 16.3],
                    [77.5, 17.1], [78.3, 18.5], [79.2, 20.2], [78.9, 21.8],
                    [77.1, 21.9], [75.5, 21.8], [74.0, 21.5], [73.0, 20.5],
                    [72.6, 18.8]
                ]]
            }
        }
    ]
}

# Create base map with no default tiles
m = folium.Map(location=center_coords, zoom_start=zoom_level, tiles=None)

# Add base layers
folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
folium.TileLayer('Stamen Terrain', name='Terrain', attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors').add_to(m)
folium.TileLayer('Stamen Toner', name='Toner', attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors').add_to(m)
folium.TileLayer('Stamen Watercolor', name='Watercolor', attr='Map tiles by Stamen Design, CC BY 3.0 — Map data © OpenStreetMap contributors').add_to(m)
folium.TileLayer('CartoDB positron', name='Light').add_to(m)
folium.TileLayer('CartoDB dark_matter', name='Dark').add_to(m)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite',
    overlay=False,
    control=True
).add_to(m)

# Add Maharashtra boundary
folium.GeoJson(maharashtra_geojson, name="Maharashtra Boundary", style_function=lambda x: {
    'fillColor': 'none',
    'color': 'black',
    'weight': 2
}).add_to(m)

# Seasonal information for different crops
seasonal_info = {
    'Wheat': 'Best grown in Winter (November to February) in cool, dry conditions.',
    'Rice': 'Best grown in the Raining season (June to September) in flooded conditions.',
    'Maize': 'Best grown in Summer (March to June) with plenty of sunlight.',
    'Sugarcane': 'Best grown in Summer (March to June), requiring a warm, sunny climate.',
    'Bajra': 'Best grown in Raining season (June to September), thrives in hot and dry regions.',
    'Cotton': 'Best grown in Summer (March to June) with a hot, dry climate.'
}

# Crop Layers
wheat_layer = folium.FeatureGroup(name='Wheat NDVI', show=True)
rice_layer = folium.FeatureGroup(name='Rice NDVI', show=False)
maize_layer = folium.FeatureGroup(name='Maize NDVI', show=False)
sugarcane_layer = folium.FeatureGroup(name='Sugarcane NDVI', show=False)
bajra_layer = folium.FeatureGroup(name='Bajra NDVI', show=False)
cotton_layer = folium.FeatureGroup(name='Cotton NDVI', show=False)

# Enhanced NDVI points with styled HTML popups
def add_ndvi_points(layer, color, crop_name, price_range):
    for _ in range(50):
        lat = random.uniform(17.5, 21.5)
        lon = random.uniform(73.0, 78.5)
        ndvi_val = random.uniform(0.2, 0.9)
        price = random.uniform(*price_range)
        season = seasonal_info.get(crop_name, "Season information not available")

        popup_html = f"""
        <div style="font-family: Arial; font-size: 13px; line-height: 1.4;">
            <h4 style="margin: 0 0 8px 0; color: {color};">{crop_name} NDVI Info</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td><strong>NDVI:</strong></td>
                    <td style="color: {'green' if ndvi_val > 0.6 else 'orange' if ndvi_val > 0.4 else 'red'};">{ndvi_val:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Price:</strong></td>
                    <td>₹{price:.2f} per kg</td>
                </tr>
                <tr>
                    <td><strong>Location:</strong></td>
                    <td>{lat:.2f}, {lon:.2f}</td>
                </tr>
                <tr>
                    <td><strong>Best Season:</strong></td>
                    <td>{season}</td>
                </tr>
            </table>
        </div>
        """

        popup = folium.Popup(folium.IFrame(html=popup_html, width=300, height=150), max_width=300)

        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.75,
            popup=popup
        ).add_to(layer)

# Assign price ranges for each crop
crop_prices = {
    'Wheat': (15, 25),
    'Rice': (30, 45),
    'Maize': (18, 30),
    'Sugarcane': (40, 60),
    'Bajra': (25, 35),
    'Cotton': (50, 75)
}

# Add NDVI points with crop prices
add_ndvi_points(wheat_layer, 'green', 'Wheat', crop_prices['Wheat'])
add_ndvi_points(rice_layer, 'yellow', 'Rice', crop_prices['Rice'])
add_ndvi_points(maize_layer, 'orange', 'Maize', crop_prices['Maize'])
add_ndvi_points(sugarcane_layer, 'purple', 'Sugarcane', crop_prices['Sugarcane'])
add_ndvi_points(bajra_layer, 'blue', 'Bajra', crop_prices['Bajra'])
add_ndvi_points(cotton_layer, 'red', 'Cotton', crop_prices['Cotton'])

# Add layers to map
for layer in [wheat_layer, rice_layer, maize_layer, sugarcane_layer, bajra_layer, cotton_layer]:
    layer.add_to(m)

# Legend Template
legend_html = """
{% macro html(this, kwargs) %}
<div id='crop-legend' style="position: fixed; top: 80px; left: 50px; z-index: 9999; background-color: white; padding: 12px; border: 2px solid grey; width: 260px; font-size: 13px;">
  <strong>Crop NDVI Legend:</strong><br><br>

  <div style="display: flex; align-items: center; margin-bottom: 6px;">
    <div style="width: 15px; height: 15px; background-color: green; margin-right: 8px; border-radius: 50%;"></div>
    <div><strong>Wheat</strong><br>Area: 14.2 lakh ha<br>Production: 120 lakh tonnes</div>
  </div>

  <div style="display: flex; align-items: center; margin-bottom: 6px;">
    <div style="width: 15px; height: 15px; background-color: yellow; margin-right: 8px; border-radius: 50%;"></div>
    <div><strong>Rice</strong><br>Area: 41.1 lakh ha<br>Production: 125 lakh tonnes</div>
  </div>

  <div style="display: flex; align-items: center; margin-bottom: 6px;">
    <div style="width: 15px; height: 15px; background-color: orange; margin-right: 8px; border-radius: 50%;"></div>
    <div><strong>Maize</strong><br>Area: 11.5 lakh ha<br>Production: 45 lakh tonnes</div>
  </div>

  <div style="display: flex; align-items: center; margin-bottom: 6px;">
    <div style="width: 15px; height: 15px; background-color: purple; margin-right: 8px; border-radius: 50%;"></div>
    <div><strong>Sugarcane</strong><br>Area: 9.3 lakh ha<br>Production: 750 lakh tonnes</div>
  </div>

  <div style="display: flex; align-items: center; margin-bottom: 6px;">
    <div style="width: 15px; height: 15px; background-color: blue; margin-right: 8px; border-radius: 50%;"></div>
    <div><strong>Bajra</strong><br>Area: 7.5 lakh ha<br>Production: 30 lakh tonnes</div>
  </div>

  <div style="display: flex; align-items: center;">
    <div style="width: 15px; height: 15px; background-color: red; margin-right: 8px; border-radius: 50%;"></div>
    <div><strong>Cotton</strong><br>Area: 42 lakh ha<br>Production: 85 lakh bales</div>
  </div>

</div>
{% endmacro %}
"""

macro = MacroElement()
macro._template = Template(legend_html)
m.get_root().add_child(macro)

# Layer control
LayerControl(collapsed=True).add_to(m)

# Save map
m.save(r"C:\Users\ASUS\Downloads\maharashtra_crop_info_map_with_prices_and_seasons.html")
print("Map with enhanced interactive popups saved as 'maharashtra_crop_info_map_with_prices_and_seasons.html'. Open it in your browser!")
