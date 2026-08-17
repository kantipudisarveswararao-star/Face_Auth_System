import os
import cv2
from log_utils import read_logs

def open_dashboard(user):
    while True:
        print("\n========== DASHBOARD ==========")
        print(f" Logged in as: {user['name']}")
        print("================================")
        print(" 1. View my registered face image")
        print(" 2. View recent access logs")
        print(" 3. Logout")
        print("================================")

        choice = input("Select an option (1-3): ").strip()

        if choice == "1":
            _show_registered_image(user)
        elif choice == "2":
            _show_logs()
        elif choice == "3":
            print(f"[INFO] Logging out {user['name']}...")
            break
        else:
            print("[ERROR] Invalid option. Try again.")

def _show_registered_image(user):
    path = user.get("image_path")
    if path and os.path.isfile(path):
        img = cv2.imread(path)
        cv2.imshow(f"Registered Face - {user['name']}", img)
        print("[INFO] Press any key on the image window to close it.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("[ERROR] Registered image not found.")

def _show_logs():
    logs = read_logs(limit=10)
    if not logs:
        print("[INFO] No access logs found.")
        return

    print("\n--- Recent Access Logs (latest first) ---")
    print(f"{'Timestamp':<20} {'User':<12} {'Status':<8} {'Distance':<10} {'Reason'}")
    print("-" * 70)
    for row in logs:
        timestamp, username, status, distance, reason = row
        print(f"{timestamp:<20} {username:<12} {status:<8} {distance:<10} {reason}")
