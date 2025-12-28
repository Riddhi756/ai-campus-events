# ai-campus-events
AI-powered Campus Events Management System

🧩 Problem Statement
Managing campus events manually often leads to missed deadlines, poor visibility of events, and low student participation.
Important event details shared through posters or PDFs are difficult to organize and track efficiently.

💡 Solution Overview
This web application automates campus event management using AI.
Admins can upload event posters or PDFs, from which AI extracts relevant information and generates concise summaries.
Students are shown only upcoming events in a clean and user-friendly dashboard.

🚀 Key Features
AI-based event text extraction (OCR + Gemini)
Automatic event summarization
Admin dashboard to upload and manage events
Student dashboard showing upcoming events only
Secure handling of credentials using environment variables

🛠 Tech Stack
Frontend: HTML, CSS, Bootstrap
Backend: Flask (Python)
Database: MySQL
AI: Google Gemini API
OCR: Tesseract OCR

⚙️ How to Run Locally

Clone the repository
git clone https://github.com/Riddhi756/ai-campus-events.git

Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Create a .env file in the project root and add:
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=
GEMINI_API_KEY=

Run the application
python app.py
Open in browser
http://127.0.0.1:5000

📸 Screenshots
#Homepage
<img width="1917" height="910" alt="image" src="https://github.com/user-attachments/assets/feadb300-c2fb-497c-ac47-f227cdf0f3d7" />

#Admin Dashboard
<img width="1918" height="906" alt="image" src="https://github.com/user-attachments/assets/fb8c6c67-ebd3-4ddd-b149-81cc8ebc27e2" />

#Student Dashboard
<img width="1887" height="907" alt="image" src="https://github.com/user-attachments/assets/a5c9acf6-a2a3-4d2d-ad20-c6b8fd61b0ce" />


