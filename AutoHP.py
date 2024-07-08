import cv2
import numpy as np
import os
import autoit
#import time
#import keyboard
import pygetwindow as gw
import pyautogui


# Define thresholds
RED_THRESHOLD = 50  # Adjust as needed
BLUE_THRESHOLD = 20  # Adjust as needed

# Flags to track if actions have been taken
red_action_taken = False
blue_action_taken = False

# Window title of your software (replace with the actual title)
TARGET_WINDOW_TITLE = "MapleLegends ("

#script_active = False
message_displayed = False

#def toggle_script():
    #global script_active
    #script_active = not script_active
    #print(f"Script is now {'active' if script_active else 'inactive'}")

#keyboard.add_hotkey('F10', toggle_script)

def get_window_region(window_title, x_offset, y_offset, width, height):

    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        left, top = window.topleft
        region = (left + x_offset, top + y_offset, width, height)
        return region
    except IndexError:
        print(f"Window with title '{window_title}' not found.")
        return None

def capture_screen(region, filename='temp_screenshot.png'):
    if region:
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save(filename)
        img = cv2.imread(filename)
        return img
    else:
        return None
    
def analyze_bars(image):
    height, width = image.shape[:2]
    mid_point = width // 2

    # Split the image into left (red) and right (blue) halves
    red_half = image[:, :mid_point]
    blue_half = image[:, mid_point:]

    # Convert the image halves from BGR to HSV color space
    hsv_red = cv2.cvtColor(red_half, cv2.COLOR_BGR2HSV)
    hsv_blue = cv2.cvtColor(blue_half, cv2.COLOR_BGR2HSV)

    # Define color ranges for red and blue
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])

    # Create masks for red and blue
    mask_red = cv2.inRange(hsv_red, lower_red, upper_red)
    mask_blue = cv2.inRange(hsv_blue, lower_blue, upper_blue)

    # Find contours in the masks
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    def calculate_level(contours, total_width):
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            fill_width = x + w  # Right edge of the contour
            percentage = (fill_width / total_width) * 100
            return percentage
        return 0

    # Calculate levels
    red_level = calculate_level(contours_red, mid_point)
    blue_level = calculate_level(contours_blue, width - mid_point)

    #red_debug = visualize_detection(red_half, contours_red)
    #blue_debug = visualize_detection(blue_half, contours_blue)
    #cv2.imshow("Red Detection", red_debug)
    #cv2.imshow("Blue Detection", blue_debug)

    return red_level, blue_level

def visualize_detection(image, contours):
    debug_image = image.copy()
    cv2.drawContours(debug_image, contours, -1, (0, 255, 0), 2)
    return debug_image

# Example usage
window_title = "MapleLegends"  # Replace with your actual window title
x_offset = 412      #
y_offset = 1404     #
width = 400         #
height = 28         #

def main():
    window_title = "MapleLegends"  # Replace with your actual window title
    x_offset = 412      #
    y_offset = 1404     #
    width = 400         #
    height = 28         #
    screenshot_filename = 'temp_screenshot.png'
    try:
        print("working?")
        if autoit.win_active(TARGET_WINDOW_TITLE):
            print("in focus")
            region = get_window_region(window_title, x_offset, y_offset, width, height)
            if region:
                    # Delete previous screenshot if it exists
                    if os.path.exists(screenshot_filename):
                        os.remove(screenshot_filename)
                    screen = capture_screen(region, screenshot_filename)
                    if screen is not None:
                        #os.system("cls")
                        red_level, blue_level = analyze_bars(screen)
                        print(f"Red level: {red_level:.2f}%, Blue level: {blue_level:.2f}%")
                        # Check red level and perform action if needed
                        if red_level < RED_THRESHOLD and not red_action_taken:
                            autoit.send("{INSERT}")
                            #time.sleep(0.5)
                        # Check blue level and perform action if needed
                    if blue_level < BLUE_THRESHOLD and not blue_action_taken:
                        autoit.send("{HOME}")
                        #time.sleep(0.5)
                    
                            
    except KeyboardInterrupt:
        print("Script terminated by user")
    finally:

        cv2.destroyAllWindows()
    
        # Clean up: delete the last screenshot
        if os.path.exists(screenshot_filename):
            os.remove(screenshot_filename)
