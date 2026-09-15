# CocoaGuard

CocoaGuard is an AI-powered cocoa disease detection and farm
monitoring system.

The system uses a YOLO object detection model to analyse cocoa
plant images and identify potential diseases.

## Current Disease Classes

- Anthracnose
- Cocoa Swollen Shoot Virus Disease (CSSVD)
- Healthy

## Features

- Farmer registration and authentication
- Farm management
- Cocoa image diagnosis
- YOLO-based disease detection
- Detection confidence scores
- Risk assessment
- Diagnosis history
- Microsoft SQL Server database integration

## Technology Stack

### Backend
- Python
- Flask
- SQLAlchemy

### Database
- Microsoft SQL Server

### Machine Learning
- Ultralytics YOLO
- PyTorch
- OpenCV

### Frontend
- HTML
- CSS
- JavaScript

## Project Structure

```text
app/
├── routes/
├── services/
├── static/
└── templates/