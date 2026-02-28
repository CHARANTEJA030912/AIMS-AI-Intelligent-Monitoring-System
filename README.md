# 🛡️ AIMS - AI Intelligent Monitoring System

A Windows-based intelligent background monitoring system with anomaly detection, risk scoring, and Telegram remote control.

## 🚀 Features
- Real-time CPU, RAM, Disk monitoring
- Isolation Forest anomaly detection
- Risk scoring engine
- Telegram remote control
- Auto high-risk alerts
- Boot & shutdown notifications

## 🛠 Tech Stack
- Python
- psutil
- scikit-learn
- SQLite
- Telegram Bot API

## 📂 Architecture
controller.py - Main engine  
core/ - Monitoring and AI logic  
telegram_bot.py - Remote control interface  

## ⚠️ Setup

1. Create `.env` file
2. Add Telegram token
3. Install requirements
4. Run controller.py