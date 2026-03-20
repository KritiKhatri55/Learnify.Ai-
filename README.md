# 🚀 Learnify.Ai : SOP to AI Training System
**Live Demo:** https://learnify-ai-bkoymha2hca3ob7kzzzsnj.streamlit.app/


## 📌 Overview
Learnify.ai is an intelligent, multimodal AI web application designed to instantly transform standard corporate documents (SOPs) into engaging, comprehensive training modules. Built as an assessment project for the AI Automation Intern role at Nutrabay, this tool bridges the gap between static text and interactive employee learning.

## ✨ Key Features
* **Instant Document Processing:** Upload any PDF SOP, and the system seamlessly extracts and analyzes the raw text.
* **Multimodal Audio Briefing:** Automatically generates and synthesizes a human-sounding audio introduction using Google Text-to-Speech (gTTS).
* **Structured AI Outputs:** Utilizes advanced prompt engineering to generate a perfectly formatted Executive Summary, Step-by-Step Guide, and 5-Question Evaluation Quiz.
* **Interactive Document Q&A:** Features a built-in AI chatbot equipped with retrieval-augmented context. It answers user queries strictly based on the uploaded SOP, preventing hallucinations.
* **Premium UI/UX:** Built with Streamlit, featuring a responsive wide layout, dynamic status indicators, clean accordion menus, and a custom Dark/Light mode toggle.

## 🛠️ Technical Architecture
* **Frontend:** Streamlit (Python)
* **LLM Inference Engine:** Groq API (`llama-3.1-8b-instant`)
* **Document Parsing:** PyPDF2
* **Audio Synthesis:** gTTS (Google Text-to-Speech)

## 🧠 Architectural Decisions & Optimizations
* **High Availability Failover:** Initially prototyped with Google Gemini, the production architecture was pivoted to Groq (Llama 3.1) to bypass strict free-tier rate limits. This ensures a stable, frictionless, and crash-free experience for end-users and evaluators.
* **Strict JSON Enforcement:** API calls to the LLM utilize `response_format={"type": "json_object"}`. This forces the model to return strictly structured data, preventing markdown hallucinations and ensuring the Streamlit UI renders perfectly every time.

