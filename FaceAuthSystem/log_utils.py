"""
log_utils.py
Handles logging of authentication attempts (Log Result step in the pipeline).
"""

import csv
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), "access_log.csv")


def log_result(username, status, similarity=None, reason=""):
    """
    Append an authentication attempt to the access log CSV.

    username:   attempted username (string)
    status:     "GRANTED" or "DENIED"
    similarity: face match distance / confidence score (float or None)
    reason:     extra detail, e.g. "Face mismatch", "Wrong password"
    """
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Username", "Status", "FaceDistance", "Reason"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            status,
            f"{similarity:.4f}" if similarity is not None else "N/A",
            reason
        ])


def read_logs(limit=20):
    """Return the most recent `limit` log entries (excluding header)."""
    if not os.path.isfile(LOG_PATH):
        return []
    with open(LOG_PATH, mode="r") as f:
        reader = list(csv.reader(f))
    rows = reader[1:] if len(reader) > 1 else []
    return rows[-limit:][::-1]  # most recent first
