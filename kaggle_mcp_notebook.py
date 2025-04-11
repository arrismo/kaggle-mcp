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
        
        # Dataset info tab
        self.dataset_name = widgets.Text(
            description="Dataset:", 
            placeholder="owner/dataset-name"
        )
        self.include_sample = widgets.Checkbox(
            description="Include sample data",
            value=False
        )
        self.dataset_button = widgets.Button(description="Get Dataset Info")
        self.dataset_button.on_click(self.on_dataset_click)
        self.dataset_output = widgets.Output()
        dataset_box = widgets.VBox([
            self.dataset_name, 
            self.include_sample, 
            self.dataset_button, 
            self.dataset_output
        ])
        
        # Competition info tab
        self.competition_name = widgets.Text(
            description="Competition:", 
            placeholder="competition-name"
        )
        self.competition_button = widgets.Button(description="Get Competition Info")
        self.competition_button.on_click(self.on_competition_click)
        self.competition_output = widgets.Output()
        competition_box = widgets.VBox([
            self.competition_name, 
            self.competition_button, 
            self.competition_output
        ])
        
        # Set up the tabs
        self.tabs.children = [search_box, dataset_box, competition_box]
        self.tabs.set_title(0, "Search")
        self.tabs.set_title(1, "Dataset Info")
        self.tabs.set_title(2, "Competition Info")
        
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
    
    def on_dataset_click(self, button):
        """Handle dataset button click"""
        with self.dataset_output:
            self.dataset_output.clear_output()
            print(f"Getting info for dataset: {self.dataset_name.value}")
            response = self.client.get_dataset_info(
                self.dataset_name.value, 
                include_sample=self.include_sample.value
            )
            
            if response and "message" in response and "context" in response["message"]:
                dataset_info = response["message"]["context"]
                self.display_dataset_info(dataset_info)
            else:
                print("Error: No dataset info returned")
    
    def on_competition_click(self, button):
        """Handle competition button click"""
        with self.competition_output:
            self.competition_output.clear_output()
            print(f"Getting info for competition: {self.competition_name.value}")
            response = self.client.get_competition_info(self.competition_name.value)
            
            if response and "message" in response and "context" in response["message"]:
                competition_info = response["message"]["context"]
                self.display_competition_info(competition_info)
            else:
                print("Error: No competition info returned")
    
    def display_search_results(self, results):
        """Display search results in a nice format"""
        html = "<h3>Search Results</h3>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += "<tr style='background-color:#f0f0f0'><th>Dataset</th><th>Title</th><th>Size</th></tr>"
        
        for i, result in enumerate(results):
            bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            html += f"<tr style='background-color:{bg_color}'>"
            html += f"<td><a href='https://www.kaggle.com/datasets/{result['ref']}'>{result['ref']}</a></td>"
            html += f"<td>{result['title']}</td>"
            html += f"<td>{result['size']}</td>"
            html += "</tr>"
        
        html += "</table>"
        display(HTML(html))
    
    def display_dataset_info(self, info):
        """Display dataset info in a nice format"""
        html = f"<h3>Dataset: {info['title']}</h3>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += f"<tr><td><b>Size:</b></td><td>{info['size']}</td></tr>"
        html += f"<tr><td><b>Last Updated:</b></td><td>{info['lastUpdated']}</td></tr>"
        html += f"<tr><td><b>Download Count:</b></td><td>{info['downloadCount']}</td></tr>"
        html += "</table>"
        
        html += "<h4>Files:</h4>"
        html += "<ul>"
        for file in info['files']:
            html += f"<li>{file['name']} ({file['size']} bytes)</li>"
        html += "</ul>"
        
        if 'sample_data' in info and info['sample_data']:
            html += "<h4>Sample Data:</h4>"
            html += "<table style='width:100%; border-collapse: collapse; font-size:0.8em'>"
            
            # Headers
            headers = info['sample_data'][0].keys()
            html += "<tr style='background-color:#f0f0f0'>"
            for header in headers:
                html += f"<th>{header}</th>"
            html += "</tr>"
            
            # Data rows
            for i, row in enumerate(info['sample_data']):
                bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
                html += f"<tr style='background-color:{bg_color}'>"
                for header in headers:
                    html += f"<td>{row[header]}</td>"
                html += "</tr>"
            
            html += "</table>"
        
        display(HTML(html))
    
    def display_competition_info(self, info):
        """Display competition info in a nice format"""
        html = f"<h3>Competition: {info['title']}</h3>"
        html += "<table style='width:100%; border-collapse: collapse;'>"
        html += f"<tr><td><b>Category:</b></td><td>{info['category']}</td></tr>"
        html += f"<tr><td><b>Deadline:</b></td><td>{info['deadline']}</td></tr>"
        html += f"<tr><td><b>Reward:</b></td><td>{info['reward']}</td></tr>"
        html += f"<tr><td><b>Team Count:</b></td><td>{info['teamCount']}</td></tr>"
        html += "</table>"
        
        html += f"<h4>Description:</h4><div>{info['description']}</div>"
        
        display(HTML(html))