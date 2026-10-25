# AI Emergency Assist

## Overview
AI Emergency Assist is an academic prototype that monitors a driver's face and eyes using a webcam. If the eyes are not detected for 10 seconds, it starts a simulated emergency sequence.

## Features
- Webcam monitoring with OpenCV
- Face and eye detection using Haar cascade classifiers
- Countdown when eyes are not detected
- Optional SMS submission through Twilio
- Monitoring logs saved to a CSV file
- Optional C++ controller demonstration

## Requirements
- Python 3
- OpenCV (`opencv-python`)
- Twilio Python package (only if sending SMS)
- A webcam
- `EmergencyController.exe` (optional, for the C++ demonstration)

Install dependencies:
```bash
pip install opencv-python
pip install twilio
```

## Setup
1. Save the Python script in a project folder.
2. Ensure the OpenCV Haar cascade files are available through the OpenCV installation.
3. (Optional) Compile the C++ controller and place `EmergencyController.exe` in the same folder as the Python script.
4. (Optional) Configure Twilio environment variables:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
5. Replace the placeholder `+91XXXXXXXXXX` in the script with the intended recipient's phone number.

Do not share Twilio credentials publicly or hard-code them into source control.

## Run
Run the script from a terminal:
```bash
python main.py
```
Replace `main.py` with the actual name of your Python file. Press **Q** in the camera window to stop monitoring.

## Output
- `emergency_log.csv`: records elapsed time, eye-detection status, program status, and timestamp.
- Console messages: show warning and simulated emergency steps.
- SMS: submitted through Twilio only when configured; submission does not guarantee delivery.

## Important Limitations
- The GPS coordinates in the script are examples; live GPS is not connected.
- Missing eye detection does not prove that the driver is asleep or unresponsive.
- Hazard lights, roadside manoeuvres, and controlled stopping are simulations only.
- The C++ executable's behavior depends on its separate source code and must be checked independently.
- This project is for demonstration and must not be used as a real vehicle safety or control system.

## Troubleshooting
- **Webcam does not open:** Check camera permissions and the `CAMERA_ID` value.
- **OpenCV classifiers fail to load:** Reinstall or update `opencv-python`.
- **SMS is not sent:** Verify Twilio credentials, sender number, account status, and recipient number.
- **C++ executable not found:** Compile the controller and place it in the project folder.
