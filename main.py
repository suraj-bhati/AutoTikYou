
import os
import time
import json

while True:
    # Step 1: Run get_data.py
    print("Running get_data.py...")
    os.system("python3 get_data.py")
    
    # Universal wait time
    print("Waiting for 10 seconds...")
    time.sleep(10)
    
    # Step 2: Check for the existence of data.json
    if os.path.exists("data.json"):
        # Step 3: Run youtube_upload.py
        print("Running youtube_upload.py...")
        os.system("python3 youtube_upload.py")
        
        # Universal wait time
        print("Waiting for 10 seconds...")
        time.sleep(10)
        
        # Step 4: Delete the downloaded video (you'll need to know the video filename)
        # os.remove("your_downloaded_video_file.mp4")
        
        # Step 5: Delete 'data.json'
        print("Deleting data.json...")
        os.remove("data.json")
        
        # Step 6: Update urls.csv
        print("Updating urls.csv...")
        with open("urls.csv", "r") as f:
            lines = f.readlines()
        with open("urls.csv", "w") as f:
            f.writelines(lines[1:])
        
        # Universal wait time
        print("Waiting for 10 seconds...")
        time.sleep(10)
        
        # Step 7: Display remaining URLs count
        remaining_count = len(lines) - 1
        print(f"Remaining URLs: {remaining_count}")
        
        # Wait 6 hours before next loop
        print("Waiting for 6 hours before next loop...")
        time.sleep(21600 * 6)  # 6 hours
        
    else:
        print("Error: data.json does not exist.")
        break

