# Skill Bridge 🤝

## Local Skill Exchange Platform

Skill Bridge is a platform that helps people connect with others in their local community to exchange skills and services.

## 🎯 Problem Statement

People often have useful skills they can teach but do not know who needs those skills.

At the same time, people may want to learn a skill but cannot easily find someone nearby who can teach them.

Skill Bridge solves this problem by connecting people based on:

- Skills they can teach
- Skills they want to learn
- Services they can provide
- Services they need
- Location

## 💡 Our Solution

Skill Bridge allows users to:

1. Register and create an account
2. Build their profile
3. Add skills they can teach
4. Add skills they want to learn
5. Add services they can provide
6. Add services they need
7. Discover compatible users
8. View other users' profiles
9. Send exchange requests
10. Accept or reject requests
11. Schedule skill exchanges
12. Complete exchanges
13. Give ratings and reviews

## 🔄 Platform Flow

User  
↓  
Register / Login  
↓  
Create Profile  
↓  
Add Skills & Services  
↓  
Explore Users  
↓  
Matching Algorithm  
↓  
Find Compatible Person  
↓  
Send Exchange Request  
↓  
Accept Request  
↓  
Schedule Exchange  
↓  
Exchange Skills  
↓  
Complete Exchange  
↓  
Give Review & Rating

## ✨ Key Features

### 👤 User Authentication

- User registration
- Secure password hashing
- Login and logout
- Session-based authentication

### 🧑 Profile Management

Users can maintain:

- Name
- Location
- Bio
- Skills they can teach
- Skills they want to learn
- Services they can provide
- Services they need

### 🎯 Skill Matching

The platform calculates a compatibility score using:

- Matching skills
- Matching services
- Location similarity

### 🤝 Exchange Requests

Users can:

- Send requests
- Accept requests
- Reject requests
- Track request status

### 📅 Exchange Scheduling

Accepted exchanges can be scheduled with:

- Date
- Time
- Online / In-person mode

### ⭐ Reviews & Ratings

After completing an exchange, users can provide:

- Rating
- Feedback
- Review

## 🧠 Matching Algorithm

| Matching Factor | Score |
|---|---:|
| Candidate offers a skill the user needs | +50 |
| Candidate needs a skill the user offers | +30 |
| Same location | +20 |
| **Maximum Score** | **100** |

## 🛠️ Technology Stack

### Frontend

- HTML
- CSS

### Backend

- Python
- Flask

### Database

- MySQL

### Security

- Werkzeug password hashing
- Environment variables using `.env`

### Development Tools

- Git
- GitHub
- Ubuntu / WSL

## 🗄️ Database

Skill Bridge uses MySQL with the following tables:

- users
- skills
- user_offers
- user_needs
- exchange_requests
- exchange_sessions
- reviews

## 🚀 How to Run

### Clone the Repository

```bash
git clone https://github.com/AejazAhammad/Skill-Bridge.git
cd skill-bridge
