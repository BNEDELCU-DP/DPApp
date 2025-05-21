"""
Flask Application for Data Analysis and Visualization

This application provides a web interface for data analysis and visualization,
allowing users to browse files, load CSV data, display images, and interact
with plots through zooming and navigation.

The application serves images as byte streams rather than disk files to reduce
disk access during operations like zooming in/out.




ADAUGAT UN BUTON CARE CALCULEAZA VALOARE DP PENTRU FISIERUL RESPECTIV

"""




import os
import io
import base64
from flask_cors import CORS
from flask import Flask, request, render_template, jsonify, send_file
import pathlib
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid GUI issues
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import welch

import logging
import sys
import matplotlib.image as mpimg

# Import custom modules for data processing
from ReadCSVFiles import *
from CoefExtraction import *
from FFTdBExtraction import *
from NoiseFloorExtraction import *

# Import Waitress WSGI server
from waitress import serve

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow all origins (for development only)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Global variables to manage the dataset and zoom state
current_data = None  # Will store the current dataset (x, y)
original_data = None  # Will store the original dataset (x, y)
current_xstart = None  # Current x-axis start value for zooming
current_xend = None  # Current x-axis end value for zooming
x_units = None  # Units for x-axis
y_units = None  # Units for y-axis
CSV_FILE_PATH = None  # Store the selected CSV file path
PNG_FILE_PATH = None  # Store the selected PNG file path

# Global variable to store the current plot image as bytes
current_plot_image = None  # Will store the current plot as bytes

def load_and_display_image(image_path):
    """
    Loads an image from the given path and returns it as bytes.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        bytes: Image data as bytes
    """
    global current_plot_image
    
    try:
        # Load image from file
        img = mpimg.imread(image_path)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(img)
        ax.axis('off')  # Hide axes
        
        # Save the processed image to a BytesIO object instead of a file
        img_bytes = io.BytesIO()
        plt.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        plt.close()  # Free memory
        
        # Reset buffer position to the beginning
        img_bytes.seek(0)
        
        # Store the image bytes in the global variable
        current_plot_image = img_bytes.getvalue()
        
        return current_plot_image
    except Exception as e:
        logging.error(f"Error loading image: {e}")
        return None


def generate_plot(xstart=None, xend=None):
    """
    Generates a plot with optional X-axis zooming and returns it as bytes.
    The Y-axis remains fixed.
    
    Args:
        xstart (float, optional): Start value for x-axis zoom
        xend (float, optional): End value for x-axis zoom
        
    Returns:
        bytes: Plot image as bytes
    """
    global current_data, current_xstart, current_xend, x_units, y_units, current_plot_image

    # Use the current dataset
    x, y = current_data

    # Apply zoom limits if provided
    if xstart is not None and xend is not None:
        mask = (x >= xstart) & (x <= xend)
        x_zoomed = x[mask]
        y_zoomed = y[mask]
    else:
        x_zoomed, y_zoomed = x, y

    # Generate the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#1e1e1e")  # Set figure background color
    ax.set_facecolor("#1e1e1e")  # Set axes background color

    # Add horizontal grid lines with color #4E6069
    ax.yaxis.grid(True, color="#4E6069", linewidth=0.5)
    
    # Plot the data with blue color and thin lines for better performance
    ax.plot(x_zoomed, y_zoomed, color="#00BFFF", linewidth=0.5)

    # Set tick and label colors
    ax.tick_params(colors="#E0E0E0")  # Set tick colors
    ax.xaxis.label.set_color("#E0E0E0")  # Set x-axis label color
    ax.yaxis.label.set_color("#E0E0E0")  # Set y-axis label color
    ax.title.set_color("#E0E0E0")  # Set title color

    # Custom font properties
    custom_font = "Arial"  # Change to any available font
    font_color = "#E0E0E0"  # Light gray text
    font_size = 11  # Adjust size

    # Set tick parameters (for numbers on axes)
    ax.tick_params(colors=font_color, labelsize=font_size)  # Tick labels
    plt.xticks(fontsize=font_size, fontname=custom_font, color=font_color)  # X-axis numbers
    plt.yticks(fontsize=font_size, fontname=custom_font, color=font_color)  # Y-axis numbers

    # Hide spines (the black border around the plot)
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Apply the current zoom limits
    if xstart is not None and xend is not None:
        ax.set_xlim(xstart, xend)
    else:
        ax.set_xlim(x.min(), x.max())  # Default to full range

    # Add axis labels if units are provided
    if x_units:
        ax.set_xlabel(f"{x_units}", fontsize=font_size, fontname=custom_font, color=font_color)
    if y_units:
        ax.set_ylabel(f"{y_units}", fontsize=font_size, fontname=custom_font, color=font_color)

    # Save to BytesIO instead of a file
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png', dpi=300)
    plt.close()  # Free memory
    
    # Reset buffer position to the beginning
    img_bytes.seek(0)
    
    # Store the image bytes in the global variable
    current_plot_image = img_bytes.getvalue()
    
    return current_plot_image

def initialize_dataset(x, y, x_units_set=None, y_units_set=None):
    """
    Initialize the dataset and set global variables for plotting.
    
    Args:
        x (array): X-axis data
        y (array): Y-axis data
        x_units_set (str, optional): Units for x-axis
        y_units_set (str, optional): Units for y-axis
    """
    global current_data, original_data, current_xstart, current_xend, y_min, y_max, x_units, y_units

    # Ensure we have valid numpy arrays
    x = np.array(x) if not isinstance(x, np.ndarray) else x
    y = np.array(y) if not isinstance(y, np.ndarray) else y

    # Set the dataset
    original_data = (x, y)
    current_data = original_data
    
    # Handle empty data case
    if len(x) == 0:
        current_xstart = 0.0
        current_xend = 1.0
    else:
        current_xstart = float(x.min())
        current_xend = float(x.max())

    # Set Y-axis range
    y_min = float(y.min()) if len(y) > 0 else 0.0
    y_max = float(y.max()) if len(y) > 0 else 1.0

    # Set units
    x_units = x_units_set
    y_units = y_units_set

@app.route('/')
def index():
    """
    Render the main page of the application.
    
    Returns:
        str: Rendered HTML template
    """
    # Create default plot if data is available
    if current_data is not None:
        generate_plot()
    return render_template('index.html')

# New endpoint to serve the plot image as a byte stream
@app.route('/plot-image')
def get_plot_image():
    """
    Serve the current plot image as a byte stream.
    
    Returns:
        Response: Flask response with the image data
    """
    global current_plot_image
    
    if current_plot_image is None:
        # Return a default image or an error response
        return jsonify({"error": "No plot available"}), 404
    
    # Return the image as a byte stream
    return send_file(
        io.BytesIO(current_plot_image),
        mimetype='image/png',
        as_attachment=False
    )

@app.route('/zoomin', methods=['POST'])
def zoom_in():
    """
    Receives zoom values, updates the image, and returns the new image URL.
    
    Returns:
        dict: JSON response with image URL
    """
    try:
        params = request.json
        xstart = float(params.get("xstart"))
        xend = float(params.get("xend"))

        # Generate the plot with the new zoom values
        generate_plot(xstart, xend)
        
        # Return the URL to the plot image endpoint
        return jsonify({"image_url": "/plot-image"})
    except Exception as e:
        logging.error(f"Error in zoom_in: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/zoomout', methods=['POST'])
def zoom_out():
    """
    Receives zoom values, updates the image, and returns the new image URL.
    
    Returns:
        dict: JSON response with image URL
    """
    global current_data
    try:
        params = request.json
        xstart = float(params.get("xstart"))
        xend = float(params.get("xend"))

        current_data = original_data  # Reset to the original dataset
        generate_plot(xstart, xend)
        
        # Return the URL to the plot image endpoint
        return jsonify({"image_url": "/plot-image"})
    except Exception as e:
        logging.error(f"Error in zoom_out: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    """
    Reset the plot to its original state.
    
    Returns:
        dict: JSON response with image URL and plot data
    """
    global current_data, current_xstart, current_xend
    
    try:
        if original_data is None:
            raise ValueError("No data loaded")
            
        current_data = original_data
        x = original_data[0]
        
        if len(x) == 0:
            current_xstart = 0.0
            current_xend = 1.0
        else:
            current_xstart = float(x.min())
            current_xend = float(x.max())
        
        generate_plot()
        
        return jsonify({
            "image_url": "/plot-image",
            "xstart": current_xstart,
            "xend": current_xend,
            "length": len(x)
        })
        
    except Exception as e:
        logging.error(f"Error in reset: {e}")
        return jsonify({
            "error": str(e),
            "xstart": 0.0,
            "xend": 1.0,
            "length": 0
        }), 500


@app.route('/api/list-directory', methods=['GET', 'POST'])
def list_directory():
    """
    List the contents of a directory for the file explorer.
    
    Returns:
        dict: JSON response with directory contents
    """
    path = request.args.get('id', '') if request.method == 'GET' else request.json.get('id', '')
    if not path or path == '#':
        path = '/Users/Bogdan/Documents/DP/'  # Or your default root directory
    
    try:
        items = []
        for entry in os.scandir(path):
            item = {
                'id': entry.path,
                'text': entry.name,
                'children': entry.is_dir(),
                'type': 'folder' if entry.is_dir() else get_file_type(entry.name)
            }
            items.append(item)
        return jsonify(items)
    except Exception as e:
        logging.error(f"Error in list_directory: {e}")
        return jsonify({'error': str(e)}), 400

def get_file_type(filename):
    """
    Determine the file type based on its extension.
    
    Args:
        filename (str): Name of the file
        
    Returns:
        str: File type identifier
    """
    ext = filename.split('.').pop().lower()
    if ext in ['csv', 'tsv']:
        return 'csv'
    elif ext in ['json', 'yaml', 'yml']:
        return 'json'
    elif ext in ['png', 'jpg', 'jpeg', 'gif']:
        return 'image'
    return 'default'

def correct_file_path(file_path):
    """
    Corrects a file path for use in Python, handling Windows-style backslashes.
    
    Args:
        file_path (str): File path to correct
        
    Returns:
        str: Corrected file path
    """
    return str(pathlib.Path(file_path).as_posix())

@app.route('/api/load-plot-img', methods=['POST'])
def load_PNG_data():
    """
    Load a PNG image file and return it as a byte stream.
    
    Returns:
        dict: JSON response with image URL
    """
    global PNG_FILE_PATH, current_plot_image
    try:
        data = request.get_json()
        PNG_FILE_PATH = correct_file_path(data.get('filePath'))

        # Check if the file exists and is a PNG
        if not PNG_FILE_PATH or not os.path.exists(PNG_FILE_PATH) or not PNG_FILE_PATH.lower().endswith('.png'):
            return jsonify({"error": "Invalid file path or file is not a PNG."}), 400

        # Load the image and store it in memory
        load_and_display_image(PNG_FILE_PATH)
             
        # Return the URL to the plot image endpoint
        return jsonify({"image_url": "/plot-image"})
    except Exception as e:
        logging.error(f"Error in load_PNG_data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/load-csv-data', methods=['POST'])
def load_CSV_data():
    """
    Load a CSV file, process the data, and generate a plot.
    
    Returns:
        dict: JSON response with image URL and plot data
    """
    global CSV_FILE_PATH, current_data, original_data, current_xstart, current_xend, x_units, y_units    

    try:
        data = request.get_json()
        CSV_FILE_PATH = correct_file_path(data.get('filePath'))

        if not CSV_FILE_PATH or not os.path.exists(CSV_FILE_PATH) or not CSV_FILE_PATH.lower().endswith('.csv'):
            return jsonify({"error": "Invalid file path or file is not a CSV."}), 400

        # Read data with error handling
        try:
            data = readCSVFile(CSV_FILE_PATH, 1, skip_rows=9)
            if len(data) == 0:
                raise ValueError("CSV file is empty")
        except Exception as e:
            logging.error(f"Error reading CSV: {e}")
            return jsonify({"error": f"Error reading CSV: {str(e)}"}), 400

        x = np.arange(len(data))
        y = np.array(data)

        initialize_dataset(x, y,
                         x_units_set="Time (s)",
                         y_units_set="Amplitude (V)")

        generate_plot()

        return jsonify({
            "image_url": "/plot-image",
            "xstart": current_xstart,
            "xend": current_xend,
            "file_path": CSV_FILE_PATH
        })

    except Exception as e:
        logging.error(f"Error in load_CSV_data: {e}")
        # Initialize with safe defaults on error
        initialize_dataset([0, 1], [0, 1])  # Dummy data
        return jsonify({
            "error": str(e),
            "xstart": 0.0,
            "xend": 1.0
        }), 500

@app.route('/api/verify-path', methods=['POST'])
def verify_path():
    """
    Verify if a path exists and is a directory.
    
    Returns:
        dict: JSON response with validation result
    """
    try:
        data = request.get_json()
        path = data.get('path', '').strip()
        
        if not path:
            return jsonify({"valid": False, "error": "Empty path provided"})
        
        # Check if path exists and is a directory
        if os.path.exists(path) and os.path.isdir(path):
            return jsonify({"valid": True})
        else:
            return jsonify({"valid": False, "error": "Path does not exist or is not a directory"})
            
    except Exception as e:
        logging.error(f"Error in verify_path: {e}")
        return jsonify({"valid": False, "error": str(e)})

@app.route('/handle-action', methods=['POST'])
def handle_action():
    data = request.get_json()
    action = data.get('action')
    
    # Process different actions
    if action == 'compute-all':
        # Your computation logic here
        return jsonify({
            'success': True,
            'message': 'All parameters computed',
            'image_url': '/new-plot-image'  # Optional updated plot
        })
    elif action == 'left-1':
        return jsonify({
            'success': True,
            'message': 'Left button 1 action completed'
        })
    # Add more actions as needed
    else:
        return jsonify({
            'success': False,
            'error': 'Unknown action'
        })

@app.route('/api/heartbeat', methods=['GET'])
def heartbeat():
    """
    Simple endpoint to verify the application is running and responsive.
    
    Returns:
        dict: Empty response with 200 status
    """
    return jsonify({"status": "ok"}), 200


if __name__ == '__main__':
    # Example 2M dataset
    np.random.seed(42)
    x = np.linspace(0, 2_000_000, 2_000_000)
    y = np.sin(2 * np.pi * (6 / 2_000_000) * x) + np.random.normal(scale=0.01, size=len(x))

    # Initialize the dataset with Y-axis range and units
    initialize_dataset(
        x, y,
        x_units_set="Samples (No)",  # X-axis units
        y_units_set="Amplitude (V)"  # Y-axis units
    )
    
    # Generate initial plot
    generate_plot()

    # Run the Flask app with Waitress WSGI server instead of the default Flask server
    print("Starting server with Waitress on http://127.0.0.1:5000")
    serve(app, host='127.0.0.1', port=5000)
    
    # The following line is commented out as we're now using Waitress instead
    # app.run(debug=True)
