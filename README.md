📝Text Toner

Text Toner is a smart text analysis and tone checking tool powered by Python (FastAPI/Flask) and Machine Learning.
It helps users analyze the tone of their messages (formal, casual, polite, assertive, etc.) and suggests improvements to match the intended communication style.

🚀 Features

🔍 Detects tone of text (formal, informal, polite, assertive, etc.)

✨ Suggests improved versions of messages

📊 Backend built with Python (FastAPI/Flask)

📱 Cross-platform frontend built with React Native

🗄️ MongoDB for storing user data & history

📡 REST API for communication between frontend and backend

🛠️ Tech Stack

Frontend: React Native

Backend: Python (FastAPI / Flask)

Database: MongoDB

ML: Hugging Face Transformers (Tone Analysis)

📂 Project Structure
text_toner/
│── backend/          # Python backend (FastAPI/Flask + ML models)
│── frontend/         # React Native mobile app
│── requirements.txt  # Python dependencies
│── README.md         # Project documentation

⚡ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/Vijay2k0517/text_toner.git
cd text_toner

2️⃣ Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate   # (Windows)
source venv/bin/activate  # (Linux/Mac)

pip install -r requirements.txt


Run the backend:

uvicorn app:app --reload


Backend will be available at: http://localhost:8000

3️⃣ Frontend Setup (React Native)
cd frontend
npm install


Run the app:

npx react-native run-android   # For Android
npx react-native run-ios       # For iOS

🌱 Branches

main → Documentation & base setup

backend → Python backend (FastAPI/Flask + ML)

frontend → React Native mobile app
