# ⚙️ Utils Directory

> **The backbone of our AI-powered recruitment email system - where all the magic happens behind the scenes**

<div align="center">

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Mistral AI](https://img.shields.io/badge/AI-Mistral-ff6b6b.svg)](https://mistral.ai/)
[![Gmail Integration](https://img.shields.io/badge/Email-Gmail-red.svg)](https://gmail.com)

</div>

---

## 🌟 Overview

The `utils/` directory contains the core utility modules that power our intelligent recruitment email generator. Each module is designed with a specific purpose, following clean architecture principles for maintainability and scalability.

## 📁 Module Breakdown

### 📊 **Data Management**

#### `data_loader.py`
- **Purpose**: Centralized configuration loading with robust error handling
- **Features**:
  - Cached JSON data loading for optimal performance
  - Automatic error detection and user-friendly error messages
  - Streamlit integration for seamless UI feedback
- **Key Functions**: `load_data()` - Loads coordinators and email templates

#### `session_manager.py`
- **Purpose**: Complete user session lifecycle management
- **Features**:
  - IST timezone-aware session tracking
  - Secure session data storage and retrieval
  - Automatic session cleanup and logout handling
- **Key Functions**: 
  - `set_user_session()` - Initialize user session
  - `is_user_logged_in()` - Check authentication status
  - `clear_user_session()` - Complete session cleanup

### 🤖 **AI & Content Generation**

#### `openrouter_client.py`
- **Purpose**: AI service initialization and management
- **Features**:
  - OpenRouter API client setup for Mistral AI access
  - Environment-based configuration loading
  - Resource caching for optimal performance
- **Model**: `mistralai/mistral-small-3.2-24b-instruct:free`

#### `prompt_generator.py`
- **Purpose**: Dynamic prompt engineering for personalized email generation
- **Features**:
  - Context-aware prompt creation based on company information
  - Flexible bullet point management (4-7 configurable points)
  - Two-stage validation system for quality assurance
- **Key Functions**:
  - `create_improved_prompt()` - Generate personalized prompts
  - `create_validation_prompt()` - Email quality validation

#### `post_processor.py`
- **Purpose**: Email formatting, cleanup, and standardization
- **Features**:
  - Intelligent bullet point count management
  - Professional email formatting with proper spacing
  - Coordinator information injection
  - Content cleanup and optimization
- **Key Functions**:
  - `fix_bullet_count()` - Ensure correct skill points
  - `post_process_mail()` - Complete email formatting

### 📧 **Communication Services**

#### `email_sender.py`
- **Purpose**: Secure email delivery via Gmail SMTP
- **Features**:
  - Gmail integration with app-specific passwords
  - Environment-based credential management
  - Comprehensive error handling and feedback
  - Draft download functionality
- **Key Functions**:
  - `send_email()` - Direct email sending
  - `send_email_with_env_credentials()` - Environment-based sending
  - `create_download_link()` - Generate download links

#### `otp_sender.py`
- **Purpose**: Complete OTP authentication system
- **Features**:
  - Secure OTP generation and storage
  - Database integration with Supabase
  - Email delivery with professional templates
  - Automatic cleanup of expired OTPs
  - IST timezone handling
- **Key Functions**:
  - `generate_and_send_otp()` - Complete OTP workflow
  - `get_otp_status()` - Real-time OTP validation
  - `cleanup_expired_otps()` - Automatic maintenance

---

## 🔧 Technical Architecture

### **Data Flow**
```
User Input → Data Loader → AI Processing → Post Processing → Email Delivery
     ↓              ↓              ↓              ↓              ↓
Session Mgmt → Config Load → Prompt Gen → Format Clean → SMTP Send
```

### **Authentication Flow**
```
Login Request → OTP Generation → Email Delivery → Verification → Session Creation
```

### **Email Generation Flow**
```
Company Info → Prompt Creation → AI Generation → Validation → Post Processing → Final Email
```

## 🛠️ Configuration

### **Environment Variables**
```env
OPENROUTER_API_KEY=your_openrouter_api_key
EMAIL_ADDRESS=your_gmail_address
EMAIL_PASSWORD=your_gmail_app_password
```

### **Key Dependencies**
- **AI Processing**: `openai`, `python-dotenv`
- **Email Services**: `smtplib`, `email.mime`
- **Data Management**: `json`, `streamlit`
- **Authentication**: `supabase`, `pytz`
- **Text Processing**: `re`, `datetime`

## 🚀 Performance Features

- **Caching**: Streamlit resource caching for API clients and data loading
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Timezone Support**: IST timezone handling for Indian users
- **Resource Management**: Efficient memory usage with proper cleanup

## 🔐 Security Features

- **Environment Variables**: Secure credential management
- **OTP Authentication**: Time-based one-time passwords
- **Session Management**: Secure session storage and cleanup
- **Input Validation**: Comprehensive input sanitization

## 📈 Monitoring & Logging

- **Session Tracking**: User activity monitoring
- **Error Logging**: Comprehensive error tracking
- **Performance Metrics**: Response time monitoring
- **Usage Analytics**: Email generation statistics

---

## 🎯 Design Principles

- **Modularity**: Each utility has a single, well-defined responsibility
- **Reliability**: Robust error handling and fallback mechanisms
- **Performance**: Optimized for speed with intelligent caching
- **Security**: Secure handling of credentials and user data
- **Maintainability**: Clean, documented code with clear interfaces

---

*Built with precision for seamless campus recruitment automation* 🎓✨