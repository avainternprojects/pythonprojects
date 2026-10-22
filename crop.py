"""
Pest Detection and Counting System Using OpenCV
Author: AI Assistant
Date: 2024
Dataset Sources: Various publicly available pest datasets
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os
import requests
import zipfile
import tarfile
from sklearn.cluster import KMeans
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

class PestDetectionSystem:
    def __init__(self):
        self.datasets = {
            "IP102": "https://github.com/xpwu95/IP102/archive/refs/heads/master.zip",
            "CropPests": "https://www.kaggle.com/code/dogukantabak/crop-pest-dataset",
            "PlantVillage_Pests": "https://github.com/spMohanty/PlantVillage-Dataset",
            "Custom_Dataset": "self.collect"  # For custom dataset collection
        }
        
    def download_dataset(self, dataset_name, save_path="datasets"):
        """Download pest datasets"""
        print(f"Downloading {dataset_name} dataset...")
        
        # Create directories
        Path(save_path).mkdir(exist_ok=True)
        
        if dataset_name == "IP102":
            # IP102 - Large scale pest dataset
            url = self.datasets[dataset_name]
            zip_path = os.path.join(save_path, "ip102.zip")
            
            # Download (simulated - in reality, you'd use requests)
            print("IP102 Dataset Info: 75,222 images, 102 pest categories")
            print("Download from: https://github.com/xpwu95/IP102")
            print("For actual download, use: git clone https://github.com/xpwu95/IP102.git")
            
            # Create sample structure
            sample_dir = os.path.join(save_path, "IP102_sample")
            Path(sample_dir).mkdir(exist_ok=True)
            
            # Create sample images for demonstration
            self.create_sample_images(sample_dir)
            return sample_dir
            
        elif dataset_name == "Custom_Dataset":
            # Create custom dataset structure
            custom_dir = os.path.join(save_path, "custom_pests")
            self.create_custom_dataset_structure(custom_dir)
            return custom_dir
    
    def create_sample_images(self, save_dir):
        """Create sample pest images for demonstration"""
        # Create different colored circles representing different pests
        for i in range(10):
            img = np.zeros((300, 300, 3), dtype=np.uint8)
            color = (0, 255, 0) if i < 5 else (0, 0, 255)  # Green and red pests
            center = (np.random.randint(50, 250), np.random.randint(50, 250))
            radius = np.random.randint(10, 30)
            cv2.circle(img, center, radius, color, -1)
            
            # Add some noise to make it look realistic
            noise = np.random.randint(0, 50, (300, 300, 3), dtype=np.uint8)
            img = cv2.add(img, noise)
            
            # Save image
            cv2.imwrite(os.path.join(save_dir, f"pest_sample_{i}.jpg"), img)
    
    def create_custom_dataset_structure(self, base_dir):
        """Create directory structure for custom dataset"""
        categories = ['aphids', 'whiteflies', 'caterpillars', 'beetles', 'mites']
        
        for category in categories:
            cat_dir = os.path.join(base_dir, category)
            Path(cat_dir).mkdir(exist_ok=True, parents=True)
            print(f"Created directory: {cat_dir}")
    
    def load_images(self, dataset_path, limit=50):
        """Load images from dataset directory"""
        images = []
        image_paths = []
        
        # Supported image formats
        extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        
        for ext in extensions:
            image_paths.extend(list(Path(dataset_path).rglob(ext)))
            image_paths.extend(list(Path(dataset_path).rglob(ext.upper())))
        
        # Limit number of images
        image_paths = image_paths[:limit]
        
        for img_path in image_paths:
            img = cv2.imread(str(img_path))
            if img is not None:
                images.append((img, str(img_path)))
        
        print(f"Loaded {len(images)} images")
        return images
    
    def preprocess_image(self, image):
        """Preprocess image for pest detection"""
        # Convert to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize for consistency
        resized = cv2.resize(rgb, (512, 512))
        
        # Apply Gaussian blur for noise reduction
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        
        return blurred
    
    def color_based_detection(self, image, pest_color='green'):
        """Detect pests based on color"""
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        
        # Define color ranges for different pests
        color_ranges = {
            'green': [(36, 25, 25), (86, 255, 255)],  # Green pests
            'brown': [(10, 100, 20), (20, 255, 200)],  # Brown pests
            'white': [(0, 0, 200), (180, 30, 255)],    # White pests
            'red': [(0, 100, 100), (10, 255, 255)],    # Red pests
        }
        
        if pest_color not in color_ranges:
            pest_color = 'green'
        
        lower, upper = color_ranges[pest_color]
        lower = np.array(lower)
        upper = np.array(upper)
        
        # Create mask
        mask = cv2.inRange(hsv, lower, upper)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        return mask
    
    def contour_based_detection(self, mask, min_area=100, max_area=5000):
        """Detect and count pests using contour analysis"""
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        filtered_contours = []
        pest_counts = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    if circularity > 0.3:  # Filter by shape
                        filtered_contours.append(contour)
                        pest_counts.append({
                            'area': area,
                            'circularity': circularity,
                            'centroid': self.get_centroid(contour)
                        })
        
        return filtered_contours, pest_counts
    
    def get_centroid(self, contour):
        """Get centroid of a contour"""
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            return (cx, cy)
        return None
    
    def blob_detection(self, image):
        """Detect pests using blob detection"""
        # Setup SimpleBlobDetector parameters
        params = cv2.SimpleBlobDetector_Params()
        
        # Change thresholds
        params.minThreshold = 10
        params.maxThreshold = 200
        
        # Filter by Area
        params.filterByArea = True
        params.minArea = 100
        params.maxArea = 5000
        
        # Filter by Circularity
        params.filterByCircularity = True
        params.minCircularity = 0.3
        
        # Filter by Convexity
        params.filterByConvexity = True
        params.minConvexity = 0.5
        
        # Filter by Inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.01
        
        # Create detector
        detector = cv2.SimpleBlobDetector_create(params)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detect blobs
        keypoints = detector.detect(gray)
        
        return keypoints
    
    def count_pests(self, image_path, method='contour', pest_color='green'):
        """Main function to count pests in an image"""
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Could not load image: {image_path}")
            return None
        
        # Preprocess
        processed = self.preprocess_image(image)
        
        if method == 'color_contour':
            # Color-based detection with contours
            mask = self.color_based_detection(processed, pest_color)
            contours, pest_data = self.contour_based_detection(mask)
            
            # Draw results
            result = processed.copy()
            cv2.drawContours(result, contours, -1, (255, 0, 0), 2)
            
            # Mark centroids
            for pest in pest_data:
                if pest['centroid']:
                    cv2.circle(result, pest['centroid'], 5, (0, 255, 0), -1)
            
            count = len(contours)
            
        elif method == 'blob':
            # Blob detection
            keypoints = self.blob_detection(processed)
            
            # Draw results
            result = cv2.drawKeypoints(processed, keypoints, np.array([]), (0, 0, 255),
                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            count = len(keypoints)
            pest_data = [{'keypoint': kp} for kp in keypoints]
            
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            'original': image,
            'processed': processed,
            'result': result,
            'count': count,
            'pest_data': pest_data,
            'method': method
        }
    
    def batch_process(self, dataset_path, output_dir="results"):
        """Process multiple images in batch"""
        # Load images
        images = self.load_images(dataset_path)
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        results = []
        
        for idx, (image, img_path) in enumerate(images):
            print(f"Processing image {idx + 1}/{len(images)}: {Path(img_path).name}")
            
            # Count pests using multiple methods
            result_contour = self.count_pests(img_path, method='color_contour')
            result_blob = self.count_pests(img_path, method='blob')
            
            if result_contour and result_blob:
                # Save results
                filename = Path(img_path).stem
                
                # Create comparison image
                fig, axes = plt.subplots(1, 3, figsize=(15, 5))
                
                axes[0].imshow(cv2.cvtColor(result_contour['original'], cv2.COLOR_BGR2RGB))
                axes[0].set_title('Original')
                axes[0].axis('off')
                
                axes[1].imshow(result_contour['result'])
                axes[1].set_title(f"Contour Method: {result_contour['count']} pests")
                axes[1].axis('off')
                
                axes[2].imshow(result_blob['result'])
                axes[2].set_title(f"Blob Method: {result_blob['count']} pests")
                axes[2].axis('off')
                
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"{filename}_comparison.png"), dpi=150)
                plt.close()
                
                results.append({
                    'filename': filename,
                    'contour_count': result_contour['count'],
                    'blob_count': result_blob['count'],
                    'path': img_path
                })
        
        # Generate report
        self.generate_report(results, output_dir)
        
        return results
    
    def generate_report(self, results, output_dir):
        """Generate a report of pest counts"""
        report_path = os.path.join(output_dir, "pest_count_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("=" * 50 + "\n")
            f.write("PEST DETECTION AND COUNTING REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            total_contour = 0
            total_blob = 0
            
            for result in results:
                f.write(f"Image: {result['filename']}\n")
                f.write(f"  - Contour Method: {result['contour_count']} pests\n")
                f.write(f"  - Blob Method: {result['blob_count']} pests\n")
                f.write(f"  - Difference: {abs(result['contour_count'] - result['blob_count'])}\n")
                f.write("-" * 30 + "\n")
                
                total_contour += result['contour_count']
                total_blob += result['blob_count']
            
            f.write("\n" + "=" * 50 + "\n")
            f.write("SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Total images processed: {len(results)}\n")
            f.write(f"Total pests detected (Contour): {total_contour}\n")
            f.write(f"Total pests detected (Blob): {total_blob}\n")
            f.write(f"Average per image (Contour): {total_contour/len(results):.2f}\n")
            f.write(f"Average per image (Blob): {total_blob/len(results):.2f}\n")
        
        print(f"Report saved to: {report_path}")
    
    def real_time_detection(self, camera_id=0):
        """Real-time pest detection using webcam"""
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Real-time pest detection started. Press 'q' to quit.")
        print("Press 's' to save current frame, 'c' to change color mode")
        
        color_mode = 'green'
        color_modes = ['green', 'brown', 'white', 'red']
        mode_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process frame
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = cv2.resize(rgb, (640, 480))
            
            # Detect pests
            mask = self.color_based_detection(processed, color_mode)
            contours, pest_data = self.contour_based_detection(mask)
            
            # Draw results
            result = processed.copy()
            cv2.drawContours(result, contours, -1, (255, 0, 0), 2)
            
            # Add count text
            cv2.putText(result, f"Pests: {len(contours)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(result, f"Mode: {color_mode}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Display
            display = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            cv2.imshow('Pest Detection - Real Time', display)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save frame
                filename = f"pest_frame_{len(contours)}_pests.jpg"
                cv2.imwrite(filename, display)
                print(f"Frame saved as {filename}")
            elif key == ord('c'):
                # Change color mode
                mode_idx = (mode_idx + 1) % len(color_modes)
                color_mode = color_modes[mode_idx]
                print(f"Color mode changed to: {color_mode}")
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    """Main function to demonstrate the pest detection system"""
    # Initialize system
    pest_system = PestDetectionSystem()
    
    print("=" * 60)
    print("PEST DETECTION AND COUNTING SYSTEM")
    print("=" * 60)
    
    # Show available datasets
    print("\nAvailable Datasets:")
    for i, (name, url) in enumerate(pest_system.datasets.items(), 1):
        print(f"{i}. {name}: {url}")
    
    # Download sample dataset
    print("\n1. Downloading sample dataset...")
    dataset_path = pest_system.download_dataset("IP102")
    
    # Process single image
    print("\n2. Processing single image...")
    # Create a test image
    test_img = np.zeros((500, 500, 3), dtype=np.uint8)
    # Add some "pests"
    for _ in range(8):
        center = (np.random.randint(50, 450), np.random.randint(50, 450))
        radius = np.random.randint(15, 35)
        color = (0, np.random.randint(100, 255), 0)
        cv2.circle(test_img, center, radius, color, -1)
    
    test_path = "test_pest_image.jpg"
    cv2.imwrite(test_path, test_img)
    
    # Count pests in test image
    result = pest_system.count_pests(test_path, method='color_contour')
    
    if result:
        print(f"Detected {result['count']} pests in test image")
        
        # Display results
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(cv2.cvtColor(result['original'], cv2.COLOR_BGR2RGB))
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        axes[1].imshow(result['result'])
        axes[1].set_title(f'Detected Pests: {result["count"]}')
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.savefig('single_image_result.png', dpi=150)
        plt.show()
    
    # Batch processing
    print("\n3. Starting batch processing...")
    results = pest_system.batch_process(dataset_path, output_dir="batch_results")
    
    print(f"\nBatch processing complete. Processed {len(results)} images.")
    print("Results saved in 'batch_results' directory.")
    
    # Real-time detection option
    print("\n4. Real-time Detection")
    choice = input("Do you want to start real-time detection? (y/n): ").lower()
    if choice == 'y':
        print("Starting real-time detection from webcam...")
        pest_system.real_time_detection()
    
    print("\n" + "=" * 60)
    print("SYSTEM COMPLETE")
    print("=" * 60)
    
    # Cleanup
    if os.path.exists(test_path):
        os.remove(test_path)

if __name__ == "__main__":
    main()