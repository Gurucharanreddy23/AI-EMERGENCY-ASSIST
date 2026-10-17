
import csv
import os
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime

import cv2

# ---------------- CONFIGURATION ----------------

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "emergency_log.csv"
CONTROLLER = BASE_DIR / "EmergencyController.exe"

CAMERA_ID = 0
RESPONSE_TIMEOUT = 10.0
EYE_WARNING_SECONDS = 1.0
LOG_INTERVAL = 0.5

ALERT_NUMBER = "+91XXXXXXXXXX"  # Replace with your alert number

# Example coordinates only. No live GPS is connected.
SIMULATED_GPS = "17.6868, 83.2185"

# ---------------- SMS ALERT ----------------


def send_emergency_sms():
    """
    Send SMS if Twilio is configured.
    Otherwise, print the prepared alert.
    """

    message = (
        "EMERGENCY ASSIST ALERT\n"
        "Possible driver unresponsiveness detected.\n"
        f"Time: {datetime.now().isoformat(timespec='seconds')}\n"
        f"Example location: {SIMULATED_GPS}\n"
        "Location is simulated and must be verified."
    )

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    sender_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, sender_number]):
        print("\nSMS NOT SENT: Twilio is not configured.")
        print("Prepared alert for:", ALERT_NUMBER)
        print(message)
        return False

    try:
        from twilio.rest import Client

        client = Client(account_sid, auth_token)

        sms = client.messages.create(
            body=message,
            from_=sender_number,
            to=ALERT_NUMBER
        )

        print("\nSMS submitted to Twilio.")
        print("Message SID:", sms.sid)
        return True

    except Exception as error:
        print("\nSMS ERROR:", error)
        return False


# ---------------- C++ CONTROLLER ----------------


def run_cpp_simulation():
    """
    Runs the academic C++ demonstration only.
    This does not control a real vehicle.
    """

    if not CONTROLLER.exists():
        print("\nC++ executable not found.")
        print("Compile emergency_controller.cpp if you need the simulation.")
        return False

    try:
        result = subprocess.run(
            [str(CONTROLLER), "0", "60"],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=15
        )

        print("\n--- C++ CONTROLLER OUTPUT ---")
        print(result.stdout)

        if result.returncode != 0:
            print("C++ error:", result.stderr)
            return False

        return True

    except (OSError, subprocess.TimeoutExpired) as error:
        print("Controller error:", error)
        return False


# ---------------- EMERGENCY SIMULATION ----------------


def run_emergency_demo():
    """
    All actions below are printed simulations.
    No physical vehicle actions are performed.
    """

    print("\n" + "=" * 48)
    print("EMERGENCY ASSIST SEQUENCE")
    print("=" * 48)

    print("\n1. Preparing emergency alert...")
    send_emergency_sms()

    print("\n2. Five simulated warning pulses:")

    for number in range(1, 6):
        print(f"Warning pulse {number}/5")
        time.sleep(0.4)

    print("\n3. Hazard lights: SIMULATED ON")

    print("\n4. Roadside manoeuvre: SIMULATED")
    print("No real service road is detected or entered.")

    print("\n5. Controlled stop: SIMULATED")
    run_cpp_simulation()

    print("\nSimulation complete.")
    print("No actual steering, braking, or lights were activated.")


# ---------------- CSV LOGGING ----------------


def save_record(writer, start_time, eye_state, status):
    elapsed = time.monotonic() - start_time

    writer.writerow([
        round(elapsed, 2),
        eye_state,
        status,
        datetime.now().isoformat(timespec="seconds")
    ])


# ---------------- MAIN CAMERA PROGRAM ----------------


def main():
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    eye_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades
        + "haarcascade_eye_tree_eyeglasses.xml"
    )

    if face_detector.empty() or eye_detector.empty():
        print("ERROR: OpenCV face/eye classifiers could not load.")
        return

    camera = cv2.VideoCapture(CAMERA_ID)

    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(CAMERA_ID, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Cannot open webcam.")
        print("Check Windows camera permissions or CAMERA_ID.")
        return

    print("=" * 48)
    print("       EMERGENCY ASSIST")
    print("=" * 48)
    print("Camera monitoring started.")
    print("Eyes detected: countdown resets.")
    print("Eyes not detected: countdown starts.")
    print("10 seconds without eye detection: emergency demo.")
    print("Press Q in the camera window to quit.")
    print("This is a software simulation only.\n")

    start_time = time.monotonic()
    eye_issue_start = None
    last_log_time = 0.0
    emergency_triggered = False

    try:
        with LOG_FILE.open(
            "w", newline="", encoding="utf-8"
        ) as logfile:

            writer = csv.writer(logfile)

            writer.writerow([
                "time_s",
                "eye_detection",
                "status",
                "timestamp"
            ])

            while True:
                success, frame = camera.read()

                if not success:
                    print("\nERROR: Failed to read camera frame.")
                    break

                now = time.monotonic()

                gray = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2GRAY
                )
                gray = cv2.equalizeHist(gray)

                faces = face_detector.detectMultiScale(
                    gray,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(80, 80)
                )

                eyes_detected = False

                # Detect the largest visible face.
                if len(faces) > 0:
                    x, y, w, h = max(
                        faces,
                        key=lambda box: box[2] * box[3]
                    )

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2
                    )

                    # Search the upper face for eyes.
                    upper_face = gray[
                        y:y + int(h * 0.65),
                        x:x + w
                    ]

                    eyes = eye_detector.detectMultiScale(
                        upper_face,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(12, 12)
                    )

                    eyes_detected = len(eyes) >= 1

                    for ex, ey, ew, eh in eyes:
                        cv2.rectangle(
                            frame,
                            (x + ex, y + ey),
                            (x + ex + ew, y + ey + eh),
                            (255, 200, 0),
                            2
                        )

                # Missing face or eyes is a proxy for an
                # attention issue, not proof of closed eyes.
                possible_issue = (
                    len(faces) == 0 or not eyes_detected
                )

                if eyes_detected:
                    # Reset countdown whenever eyes are detected.
                    eye_issue_start = None
                    status = "MONITORING"
                    countdown_text = "Countdown reset"

                elif possible_issue:
                    # Start countdown on the first bad frame.
                    if eye_issue_start is None:
                        eye_issue_start = now
                        print(
                            "\nEyes not detected. "
                            "Starting 10-second countdown."
                        )

                    elapsed_issue = now - eye_issue_start
                    remaining = max(
                        0.0,
                        RESPONSE_TIMEOUT - elapsed_issue
                    )

                    if elapsed_issue < EYE_WARNING_SECONDS:
                        status = "CHECKING"
                    elif elapsed_issue < RESPONSE_TIMEOUT:
                        status = "WARNING"
                    else:
                        status = "EMERGENCY"

                    countdown_text = (
                        f"Time remaining: {remaining:.1f}s"
                    )

                else:
                    status = "MONITORING"
                    countdown_text = "Monitoring"

                # Draw status on camera window.
                color = (
                    (0, 0, 255)
                    if status in ("WARNING", "EMERGENCY")
                    else (0, 255, 0)
                )

                cv2.putText(
                    frame,
                    "Status: " + status,
                    (15, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )

                cv2.putText(
                    frame,
                    "Eyes detected: " + str(eyes_detected),
                    (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    countdown_text,
                    (15, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Q = quit | Simulation only",
                    (15, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1
                )

                # Log periodically.
                if now - last_log_time >= LOG_INTERVAL:
                    eye_state = (
                        "DETECTED"
                        if eyes_detected
                        else "NOT_DETECTED"
                    )

                    save_record(
                        writer,
                        start_time,
                        eye_state,
                        status
                    )

                    logfile.flush()
                    last_log_time = now

                cv2.imshow(
                    "Emergency Assist - Driver Monitor",
                    frame
                )

                # The break is inside the while loop.
                if (
                    status == "EMERGENCY"
                    and not emergency_triggered
                ):
                    emergency_triggered = True

                    save_record(
                        writer,
                        start_time,
                        "NOT_DETECTED",
                        "EMERGENCY_SEQUENCE"
                    )
                    logfile.flush()

                    print(
                        "\n10 seconds elapsed without "
                        "eye detection."
                    )

                    # Stop camera processing before sequence.
                    break

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("\nMonitoring stopped by user.")
                    break

    except KeyboardInterrupt:
        print("\nProgram interrupted.")

    except OSError as error:
        print("\nFile error:", error)

    finally:
        camera.release()
        cv2.destroyAllWindows()

    # Run after leaving the camera loop.
    if emergency_triggered:
        run_emergency_demo()

    print("\nCSV log saved to:", LOG_FILE)
    print("Emergency Assist program ended.")


if __name__ == "__main__":
    main()
