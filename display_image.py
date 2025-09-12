import cv2
import os
from pathlib import Path
import shutil
import numpy as np

def check_and_create_image_dir(base_dir):
    """Create images directory if it doesn't exist"""
    image_dir = Path(base_dir) / "images"
    image_dir.mkdir(exist_ok=True)
    print(f"Using images directory: {image_dir}")
    return image_dir

def copy_sample_image(source_path, dest_path):
    """Copy a sample image to the images directory"""
    try:
        shutil.copy2(source_path, dest_path)
        print(f"Successfully copied image to: {dest_path}")
        return True
    except shutil.SameFileError:
        print("Image already exists in the destination")
        return True
    except Exception as e:
        print(f"Error copying image: {e}")
        return False

def load_and_display_image(image_path):
    """
    Loads an image from the specified path and displays it in a window.
    Handles Unicode paths by reading the file as binary data first.
    """
    try:
        # Read file as binary first
        with open(image_path, 'rb') as f:
            image_binary = np.asarray(bytearray(f.read()), dtype=np.uint8)
            img = cv2.imdecode(image_binary, cv2.IMREAD_COLOR)
        
        if img is None:
            print(f"Error: Could not decode image at {image_path}")
            print(f"File exists: {Path(image_path).exists()}")
            return False

        # Display image
        window_name = 'Image Display'
        cv2.imshow(window_name, img)
        print("Image displayed. Press any key to close the window.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return True

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    # Get the script directory
    script_dir = Path(__file__).parent.resolve()
    
    # Ensure images directory exists
    image_dir = check_and_create_image_dir(script_dir)
    
    # Set up image paths
    sample_image = "sample_image.png"
    image_path = image_dir / sample_image
    
    if not image_path.is_file():
        print("\nNo image found. Please provide an image using one of these methods:")
        print("1. Place any image in the 'images' folder")
        print("2. Update the script with your image filename")
        print(f"\nImages folder: {image_dir}")
        print("Expected image name: sample_image.png")
    else:
        load_and_display_image(image_path)
