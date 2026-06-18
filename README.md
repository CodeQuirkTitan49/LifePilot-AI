# 🚀 LifePilot AI

**LifePilot AI** is an AI-powered life administration assistant that helps users manage important documents effortlessly. By leveraging **Google Gemini AI**, the application analyzes PDFs and images, extracts key information, identifies deadlines, generates actionable tasks, and integrates with Google Calendar to keep users organized.

## 📌 Problem Statement

Managing important documents such as utility bills, bank statements, government notices, insurance documents, and renewal reminders can be overwhelming. Important dates and actions are often missed, leading to penalties, missed payments, or delayed responses.

LifePilot AI addresses this challenge by automatically analyzing documents and converting them into actionable insights.

---

## ✨ Features

* 📄 Upload PDF and Image Documents
* 🤖 AI-Powered Document Analysis using Gemini AI
* 📝 Automatic Document Summarization
* 🏷️ Document Type Identification
* 📅 Important Date & Deadline Extraction
* ✅ Suggested Action Generation
* 📊 Task Progress Tracking
* 🗂️ Document Archiving System
* 💾 Persistent Storage using SQLite
* 📆 Google Calendar Integration
* 🌐 Deployed Streamlit Web Application

---

## 🛠️ Tech Stack

### Frontend

* Streamlit

### Backend

* Python

### AI & Processing

* Google Gemini AI
* PyMuPDF (PDF Processing)
* Pillow (Image Handling)

### Database

* SQLite

### Integrations

* Google Calendar API

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/CodeQuirkTitan49/LifePilot-AI.git
cd LifePilot-AI
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Run the Application

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```text
LifePilot-AI/
│
├── app.py
├── requirements.txt
├── lifepilot.db
├── README.md
└── assets/
```

---

## 🔄 Workflow

1. User uploads a PDF or image document.
2. Text is extracted from the document.
3. Gemini AI analyzes the content.
4. The system:

   * Identifies document type
   * Generates a summary
   * Extracts important dates
   * Suggests actions
5. Users can save and track documents.
6. Tasks are stored and progress is monitored.
7. Important events can be added to Google Calendar.

---

## 🎯 Future Enhancements

* OCR support for scanned documents
* User authentication
* Cloud database integration
* Email drafting assistance
* Reminder notifications
* Mobile application support
* Multi-calendar synchronization

---

## 👩‍💻 Developer

**Samyuktha Jannu**

B.Tech (Computer Science & Engineering)
2nd Year
CMR Technical Campus

GitHub: https://github.com/CodeQuirkTitan49

LinkedIn: https://www.linkedin.com/in/samyuktha-jannu-127101327

---

## 📜 License

This project is developed for educational and research purposes.
