import cv2
import face_recognition
import numpy as np
from keras_facenet import FaceNet

# Initialize FaceNet model
facenet_model = FaceNet()
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Threshold for deciding whether two faces match (lower = stricter)
FACE_MATCH_THRESHOLD = 0.45

def detect_faces_haar(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    return faces

def get_face_encoding(frame):

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")

    if len(face_locations) == 0:
        return None, "No face detected. Please face the camera clearly."
    if len(face_locations) > 1:
        return None, "Multiple faces detected. Only one person should be in frame."

    encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    if len(encodings) == 0:
        return None, "Could not extract facial features. Try again with better lighting."

    return encodings[0], face_locations[0]


def compare_faces(known_encoding, unknown_encoding):
    """
    Compare with Database step.
    Returns (is_match: bool, distance: float)
    Smaller distance = more similar face. Threshold defines the cutoff.
    """
    distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
    is_match = distance <= FACE_MATCH_THRESHOLD
    return is_match, float(distance)


def find_best_match(unknown_encoding, all_users):

    if len(all_users) == 0:
        return None, 1.0

    known_encodings = [u["face_encoding"] for u in all_users]
    distances = face_recognition.face_distance(known_encodings, unknown_encoding)

    best_index = int(np.argmin(distances))
    best_distance = float(distances[best_index])

    if best_distance <= FACE_MATCH_THRESHOLD:
        return all_users[best_index], best_distance
    return None, best_distance


def draw_face_box(frame, location, label="", color=(0, 255, 0)):
    """Draw a bounding box and label on the frame around a detected face."""
    top, right, bottom, left = location
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
    if label:
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, label, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    return frame
