import cv2
import time
import getpass
from database import init_db, get_user_by_name
from face_utils import get_face_encoding, compare_faces, detect_faces_haar, draw_face_box
from log_utils import log_result
from dashboard import open_dashboard


def login_user():
    init_db()

    name = input("Enter your username: ").strip()
    user = get_user_by_name(name)

    if user is None:
        print("[ERROR] User not found.")
        log_result(name, "DENIED", reason="Username not found")
        return

    password = getpass.getpass("Enter your password: ").strip()

    print("\n[INFO] Opening webcam for face verification...")
    print("Look at the camera. Press 'v' to verify, 'q' to cancel.\n")

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

        cv2.putText(display_frame, "Press 'v' to verify | 'q' to cancel",
                    (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Login - Face Verification", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('v'):
            captured_frame = frame.copy()
            break
        elif key == ord('q'):
            print("[INFO] Login cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()
    cv2.destroyAllWindows()

    if captured_frame is None:
        print("[ERROR] No frame captured.")
        return

    print("[INFO] Detecting face and extracting features...")
    result = get_face_encoding(captured_frame)
    encoding, info = result

    if encoding is None:
        print(f"[DENIED] {info}")
        log_result(name, "DENIED", reason=f"Face extraction failed: {info}")
        print(" ACCESS DENIED")
        return

    print("[INFO] Comparing with stored face data...")
    face_match, distance = compare_faces(user["face_encoding"], encoding)
    password_match = (password == user["password"])

    print(f"[INFO] Face distance: {distance:.4f} (threshold = 0.45)")
    print(f"[INFO] Face match: {face_match} | Password match: {password_match}")

    if face_match and password_match:
        print(f" ACCESS GRANTED. Welcome, {user['name']}!")
        log_result(name, "GRANTED", similarity=distance, reason="Face and password matched")
        time.sleep(1)
        open_dashboard(user)
    else:
        reasons = []
        if not face_match:
            reasons.append("Face mismatch")
        if not password_match:
            reasons.append("Wrong password")
        reason_text = ", ".join(reasons)

        print(" ACCESS DENIED")
        print(f" Reason: {reason_text}")
        log_result(name, "DENIED", similarity=distance, reason=reason_text)


if __name__ == "__main__":
    login_user()
