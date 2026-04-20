# 🚀 AI-Adaptive Onboarding Engine

## 📌 Overview

The AI-Adaptive Onboarding Engine is an intelligent system that personalizes employee onboarding using AI, real-world datasets, and graph-based learning.

It analyzes a candidate’s resume against a job description to generate a **dynamic, adaptive learning roadmap**, reducing redundant training and improving efficiency.

---

## 🎯 Problem Statement

Traditional onboarding systems:

* Follow a one-size-fits-all approach ❌
* Waste time on already known skills ❌
* Lack personalization ❌

### ✅ Our Solution:

* Extracts skills using AI
* Identifies skill gaps
* Generates adaptive learning paths
* Uses real datasets to ensure reliability

---

## 🧠 Key Features

### 🔍 Intelligent Skill Extraction

* Uses LLM (GPT-3.5) to extract skills from Resume & JD

### 📊 Dataset-Grounded Validation (🔥 Unique)

* Uses Resume Dataset to build a real-world skill database
* Filters AI outputs to reduce hallucinations

### ⚖️ Skill Gap Analysis

* Identifies missing skills required for the job

### 🕸️ Graph-Based Learning Path

* Skill dependencies modeled using NetworkX
* Generates structured, prerequisite-aware roadmap

### 🧠 Reasoning Trace

* Explains why each skill is recommended

### 🎯 Hire Readiness Score

* Shows % match between candidate and job

### 📊 Skill Progress Visualization

* Visual progress bars for skill coverage

### ⏱️ Learning Time Estimation

* Predicts time required to complete roadmap

### 📚 Course Recommendations

* Suggests relevant learning resources

### 🤖 AI Career Mentor

* Chatbot for career guidance and learning advice

---

## 🏗️ Architecture

Resume + JD
↓
Skill Extraction (LLM)
↓
Dataset Validation
↓
Skill Gap Detection
↓
Skill Graph Mapping
↓
Adaptive Learning Path
↓
UI Dashboard

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **LLM:** OpenAI (GPT-3.5 Turbo)
* **Graph Engine:** NetworkX
* **Visualization:** PyVis
* **Data Processing:** Pandas
* **Environment:** Python-dotenv

---

## 📊 Datasets Used

* 📄 Resume Dataset (Kaggle)
* 💼 Job Description Dataset
* 🧠 O*NET Skills Database

👉 Used to:

* Build skill vocabulary
* Validate extracted skills
* Improve system accuracy

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/yourusername/ai-onboarding-engine.git
cd ai-onboarding-engine

python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` file:

```env
OPENAI_API_KEY= "AIzaSyCxouXj-KQQ5ir_7L8Yor3IxIWNebI0uTU"
```

Run app:

```bash
streamlit run app.py
```

---

## 🐳 Docker Setup

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 📈 Evaluation Metrics

* Skill Match Accuracy
* Learning Time Reduction
* Path Efficiency
* User Experience Score
* System Reliability (Dataset-grounded)

---

## 🚀 Unique Contributions

* 🔥 Dataset-grounded AI (reduces hallucination)
* 🔥 Graph-based adaptive learning
* 🔥 Real-time skill gap reasoning
* 🔥 End-to-end intelligent onboarding system

---

## 🔮 Future Improvements

* LMS integration
* Real-time progress tracking
* Multi-domain expansion
* Personalized assessments

---

## 👨‍💻 Author : Dhurandhar Team , YCCE

Hackathon Submission – AI-Adaptive Onboarding Engine 🚀
