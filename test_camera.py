#!/usr/bin/env python3
"""
Simple camera test script to verify camera access
"""
import cv2
import sys

def test_camera(camera_index=0):
    """Test if camera is accessible"""
    print(f"Testing camera {camera_index}...")
    print("Note: macOS will prompt for camera permission if not already granted.")
    print("Please grant camera access when prompted.\n")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ ERROR: Could not open camera {camera_index}")
        print("\nPossible issues:")
        print("1. Camera permission not granted - check System Settings > Privacy & Security > Camera")
        print("2. Camera is being used by another application")
        print("3. Camera index is incorrect - try 0, 1, or 2")
        return False
    
    print(f"✓ Camera {camera_index} opened successfully!")
    print("Reading a test frame...")
    
    ret, frame = cap.read()
    if not ret:
        print("❌ ERROR: Could not read frame from camera")
        cap.release()
        return False
    
    print(f"✓ Frame captured successfully! Size: {frame.shape}")
    print(f"  Width: {frame.shape[1]}px, Height: {frame.shape[0]}px")
    
    # Try to display the frame
    print("\nDisplaying camera feed for 3 seconds...")
    print("Press 'q' to quit early")
    
    import time
    start_time = time.time()
    while time.time() - start_time < 3:
        ret, frame = cap.read()
        if not ret:
            print("❌ Lost connection to camera")
            break
        
        cv2.putText(frame, "Camera Test - Press 'q' to quit", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Camera Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print("\n✅ Camera test completed successfully!")
    return True

if __name__ == "__main__":
    camera_index = 0
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
        except ValueError:
            print(f"Invalid camera index: {sys.argv[1]}. Using default: 0")
    
    success = test_camera(camera_index)
    sys.exit(0 if success else 1)

