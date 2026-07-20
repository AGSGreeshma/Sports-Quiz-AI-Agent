# 🏆 Sports Quiz AI

An AI-powered Sports Quiz Generator built using **Streamlit**, **Google Gemini**, **ChromaDB**, and **DuckDuckGo Search**. Generate interactive multiple-choice quizzes across a variety of sports with AI-generated questions, correct answers, and detailed explanations.

---

## 🌐 Live Demo

**App:** https://sports-quiz-ai-agent-njt6khpwr5nahkcyddgplf.streamlit.app/

**GitHub Repository:** https://github.com/AGSGreeshma/Sports-Quiz-AI-Agent

---

## 🎯 About the Project

Sports Quiz AI is an AI-powered quiz generation application that combines **Retrieval-Augmented Generation (RAG)**, **vector search**, **live web search**, and **Google Gemini** to create accurate and engaging sports quizzes. Users can customize quizzes by selecting a sport, difficulty level, and number of questions, while the application generates multiple-choice questions with explanations in real time.

This project demonstrates the integration of modern AI technologies into an interactive educational application with a clean and responsive user interface.

---

## 🚀 Features

- 🧠 AI-generated sports quizzes using Google Gemini
- 📚 Retrieval-Augmented Generation (RAG) with ChromaDB
- 🔎 Live web search integration using DuckDuckGo
- 📝 Multiple-choice questions with explanations
- 🎯 Three difficulty levels:
  - Easy
  - Medium
  - Hard
- ❓ Generate up to 20 quiz questions
- 🔄 Regenerate quizzes instantly
- 📥 Download generated quizzes
- 📱 Responsive modern Streamlit interface
- 🌙 Supports both Light and Dark mode

---

## 🏅 Supported Sports

- 🏏 Cricket
- ⚽ Football
- 🏀 Basketball
- 🎾 Tennis
- 🏅 Olympics
- 🏎️ Formula 1
- 🏐 Volleyball
- 🏑 Field Hockey
- 🏊 Swimming
- 🏃 Athletics (Track & Field)

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | Streamlit |
| **Programming Language** | Python |
| **AI Model** | Google Gemini |
| **Retrieval** | ChromaDB, Sentence Transformers |
| **Web Search** | DuckDuckGo Search |
| **Version Control** | Git, GitHub |

---

## 📂 Project Structure

```text
Sports-Quiz-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
├── chroma_db/
│
└── src/
    ├── agents/
    ├── config/
    ├── database/
    ├── models/
    ├── prompts/
    ├── search/
    └── utils/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/AGSGreeshma/Sports-Quiz-AI-Agent.git
cd Sports-Quiz-AI-Agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

### 5. Load the Knowledge Base

```bash
python src/database/load_data.py
```

---

### 6. Run the Application

```bash
streamlit run app.py
```

---

## 🧠 How It Works

1. User selects a sport, difficulty level, and number of questions.
2. Relevant information is retrieved from the ChromaDB knowledge base.
3. Live information is fetched using DuckDuckGo Search.
4. A structured prompt is created and sent to Google Gemini.
5. Gemini generates multiple-choice quiz questions with correct answers and explanations.
6. Results are displayed in a modern interactive interface.

---

## 📸 Screenshots

### 🏠 Home Page

The landing page where users can select a sport, difficulty level, and the number of quiz questions.

![Home Page](images/home.png)

---

### 🎛️ Sidebar

A clean and responsive sidebar for configuring quiz preferences and navigating the application.

![Sidebar](images/sidebar.png)

---

### ❓ Generated Quiz

AI-generated multiple-choice sports quiz with answer options and explanations.

![Generated Quiz](images/quiz.png)

---

### 📊 Quiz Results

Interactive results page displaying the user's score, correct answers, and explanations.

![Quiz Results](images/result.png)

---

### 🌙 Dark Mode

The application supports both Light and Dark themes for a better user experience.

![Dark Mode](images/darkmode.png)

---

### 🦶 Footer

A responsive footer with project information and useful links.

![Footer](images/footer.png)

---

## 🔮 Future Improvements

- User authentication
- Quiz timer
- Score tracking
- Leaderboards
- More sports
- Multiplayer quizzes
- Voice-based quizzes
- Difficulty recommendations

---

## 👩‍💻 Author

**Gayathri Sai Greeshma Anantha**

Computer Science Engineering (AI & ML)

---

## 📄 License

This project is licensed under the **MIT License**. 

---
