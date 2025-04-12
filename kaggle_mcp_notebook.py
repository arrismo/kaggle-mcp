import ipywidgets as widgets
from IPython.display import display, HTML
import json
from client import KaggleMCPClient

class KaggleMCPNotebook:
    def __init__(self, server_url="http://localhost:8000"):
        self.client = KaggleMCPClient(server_url)
        self.setup_ui()
    
    def setup_ui(self):
        """Create the notebook UI"""
        # Create tabs for different features
        self.tabs = widgets.Tab()
        
        # Search tab
        self.search_query = widgets.Text(description="Query:", placeholder="Enter search terms")
        self.search_button = widgets.Button(description="Search Datasets")
        self.search_button.on_click(self.on_search_click)
        self.search_output = widgets.Output()
        search_box = widgets.VBox([self.search_query, self.search_button, self.search_output])
        
        # Set up the tabs
        self.tabs.children = [search_box]
        self.tabs.set_title(0, "Search")
        
        # Display the UI
        display(self.tabs)
    
    def on_search_click(self, button):
        """Handle search button click"""
        with self.search_output:
            self.search_output.clear_output()
            print(f"Searching for: {self.search_query.value}")
            response = self.client.search_datasets(self.search_query.value)
            
            if response and "message" in response and "context" in response["message"]:
                results = response["message"]["context"]["results"]
                self.display_search_results(results)
            else:
                print("Error: No results returned")
    
    def display_search_results(self, results):
        """Display search results in a nice format"""
        html = "<h3>Search Results</h3>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='background-color:#f0f0f0'><th>Dataset</th><th>Title</th><th>Description</th><th>Downloads</th><th>Last Updated</th><th>Usability Rating</th></tr>"
        
        for i, result in enumerate(results):
            bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color:{bg_color}'>"
            html += f"<td><a href='https://www.kaggle.com/datasets/{result['ref']}'>{result['ref']}</a></td>"
            html += f"<td>{result['title']}</td>"
            html += f"<td>{result['subtitle']}</td>"
            html += f"<td>{result['download_count']}</td>"
            html += f"<td>{result['last_updated']}</td>"
            html += f"<td>{result['usability_rating'] * 10:.1f}</td>"
            html += "</tr>"
        
        html += "</table>"
        display(HTML(html))