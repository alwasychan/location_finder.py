import tkinter as tk
from tkinter import ttk, messagebox
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderServiceError
import requests
import webbrowser
import os

class LocationFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Location Finder")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize geolocator
        try:
            self.geolocator = Nominatim(user_agent="location_finder_app")
        except:
            self.geolocator = None
            messagebox.showerror("Error", "Geocoding service unavailable")
        
        # Create GUI elements
        self.create_widgets()
        
        # Try to get current location on startup
        self.find_my_location()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Location Finder", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Current location section
        loc_frame = ttk.LabelFrame(main_frame, text="Current Location", padding="10")
        loc_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        loc_frame.columnconfigure(1, weight=1)
        
        ttk.Button(loc_frame, text="Find My Location", command=self.find_my_location).grid(row=0, column=0, padx=(0, 10))
        self.location_var = tk.StringVar()
        ttk.Entry(loc_frame, textvariable=self.location_var, state="readonly", width=50).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Search section
        search_frame = ttk.LabelFrame(main_frame, text="Search Location", padding="10")
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Enter address:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=50)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        search_entry.bind("<Return>", lambda e: self.search_location())
        
        ttk.Button(search_frame, text="Search", command=self.search_location).grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Location Details", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(5, weight=1)
        
        ttk.Label(results_frame, text="Address:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.address_var = tk.StringVar()
        ttk.Entry(results_frame, textvariable=self.address_var, state="readonly", width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(results_frame, text="Coordinates:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.coords_var = tk.StringVar()
        ttk.Entry(results_frame, textvariable=self.coords_var, state="readonly").grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(results_frame, text="Map View:").grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        
        map_buttons_frame = ttk.Frame(results_frame)
        map_buttons_frame.grid(row=2, column=1, sticky=tk.W, pady=(5, 5))
        
        ttk.Button(map_buttons_frame, text="Open in Google Maps", command=self.open_google_maps).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(map_buttons_frame, text="Open in OpenStreetMap", command=self.open_osm).grid(row=0, column=1)
        
        # Add some padding to all children of main frame
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)
    
    def find_my_location(self):
        try:
            # Get approximate location based on IP
            response = requests.get('https://ipapi.co/json/', timeout=5)
            data = response.json()
            
            lat = data.get('latitude')
            lon = data.get('longitude')
            city = data.get('city')
            country = data.get('country_name')
            
            if lat and lon:
                # Get more detailed address using geopy
                if self.geolocator:
                    location = self.geolocator.reverse(f"{lat}, {lon}")
                    if location:
                        address = location.address
                    else:
                        address = f"{city}, {country}"
                else:
                    address = f"{city}, {country}"
                
                self.location_var.set(address)
                self.display_location_details(address, (lat, lon))
            else:
                messagebox.showerror("Error", "Could not determine your location")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get location: {str(e)}")
    
    def search_location(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter an address to search")
            return
        
        try:
            if self.geolocator:
                location = self.geolocator.geocode(query)
                if location:
                    self.display_location_details(location.address, (location.latitude, location.longitude))
                else:
                    messagebox.showinfo("Not Found", "Location not found. Please try a different search term.")
            else:
                messagebox.showerror("Error", "Geocoding service unavailable")
                
        except (GeocoderUnavailable, GeocoderServiceError):
            messagebox.showerror("Error", "Geocoding service is currently unavailable")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def display_location_details(self, address, coords):
        self.address_var.set(address)
        self.coords_var.set(f"Latitude: {coords[0]:.6f}, Longitude: {coords[1]:.6f}")
        self.current_coords = coords
    
    def open_google_maps(self):
        if hasattr(self, 'current_coords'):
            lat, lon = self.current_coords
            url = f"https://www.google.com/maps?q={lat},{lon}"
            webbrowser.open(url)
        else:
            messagebox.showwarning("Warning", "No location data available")
    
    def open_osm(self):
        if hasattr(self, 'current_coords'):
            lat, lon = self.current_coords
            url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}"
            webbrowser.open(url)
        else:
            messagebox.showwarning("Warning", "No location data available")

if __name__ == "__main__":
    root = tk.Tk()
    app = LocationFinderApp(root)
    root.mainloop()
