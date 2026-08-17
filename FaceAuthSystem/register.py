import cv2
import os
import getpass
from database import init_db, add_user, username_exists
from face_utils import get_face_encoding, detect_faces_haar, draw_face_box
from log_utils import log_result

DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")

def register_user():
    init_db()

    name = input("Enter your name (username): ").strip()

    if not name:
        print("[ERROR] Name cannot be empty.")
        return

    if username_exists(name):
        print(f"[ERROR] Username '{name}' already exists. Choose another.")
        return

    password = getpass.getpass("Set a password: ").strip()
    confirm = getpass.getpass("Confirm password: ").strip()

    if password != confirm:
        print("[ERROR] Passwords do not match.")
        return

    if len(password) < 4:
        print("[ERROR] Password must be at least 4 characters.")
        return

    print("\n[INFO] Opening webcam for face capture...")
    print("Position your face inside the frame.")
    print("Press 'c' to capture, 'q' to cancel.\n")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not access webcam.")
        return

    captured_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read from webcam.")
            break

        display_frame = frame.copy()
        faces = detect_faces_haar(display_frame)
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.putText(display_frame, "Press 'c' to capture | 'q' to cancel",
                    (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Register - Face Capture", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            captured_frame = frame.copy()
            break
        elif key == ord('q'):
            print("[INFO] Registration cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    if captured_frame is None:
        print("[ERROR] No frame captured.")
        return

    print("[INFO] Extracting facial features...")
    result = get_face_encoding(captured_frame)
    encoding, info = result

    if encoding is None:
        print(f"[ERROR] {info}")
        log_result(name, "DENIED", reason=f"Registration failed: {info}")
        return

    # Save the captured face image
    os.makedirs(DATASET_DIR, exist_ok=True)
    image_path = os.path.join(DATASET_DIR, f"{name}.jpg")
    cv2.imwrite(image_path, captured_frame)

    # Store in database
    success = add_user(name, password, encoding, image_path)
    if success:
        print(f"\n[SUCCESS] User '{name}' registered successfully!")
        print(f"[INFO] Face image saved to: {image_path}")
        log_result(name, "GRANTED", reason="New user registered")
    else:
        print("[ERROR] Registration failed (username may already exist).")
        log_result(name, "DENIED", reason="Registration failed - duplicate username")


if __name__ == "__main__":
    register_user()
