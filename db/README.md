# 🗄️ Database Module

<div align="center">

[![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=flat-square&logo=supabase)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)](https://python.org)
[![Security](https://img.shields.io/badge/Security-bcrypt-red?style=flat-square&logo=security)](https://pypi.org/project/bcrypt/)

**🔐 Secure Authentication & Database Management**

*Production-ready authentication system with OTP verification and session management*

</div>

---

## 🚀 Overview

The `db/` module provides a comprehensive authentication and database management system for the Lets Connect application. Built with security-first principles and modern practices.

## 📁 Module Structure

```
db/
├── auth.py         # 🔐 Core authentication logic
├── database.py     # 🗃️ Database operations & connection
├── otp.py          # 📱 OTP generation & verification
└── verify.py       # ✅ User verification workflows
```

## ⚡ Key Features

### 🔐 **Authentication**
- **Secure Password Hashing**: bcrypt-based password protection
- **User Verification**: Email-based user validation
- **Session Management**: Secure session creation and tracking
- **Activity Logging**: Comprehensive user activity monitoring

### 📱 **OTP System**
- **Time-based OTP**: Secure one-time password generation
- **Expiry Management**: Automatic OTP expiration and cleanup
- **IST Timezone**: Indian Standard Time support
- **Verification Flow**: Complete OTP verification workflow

### 🗃️ **Database Operations**
- **Supabase Integration**: Cloud-native database connectivity
- **User Management**: Complete user CRUD operations
- **Activity Tracking**: Detailed user and mail activity logs
- **Connection Pooling**: Efficient database connection management

### ✅ **Verification System**
- **Multi-step Verification**: Secure user verification process
- **OTP Validation**: Real-time OTP validity checking
- **Session Cleanup**: Automatic cleanup of expired sessions
- **Error Handling**: Robust error management and logging

## 🛠️ Quick Start

### Environment Setup
```bash
# Required environment variables
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### Basic Usage
```python
from db.auth import authenticate_user
from db.otp import verify_otp
from db.database import get_user_by_email

# Authenticate user
success, message, user_data = authenticate_user(email, password)

# Verify OTP
success, message, user_data = verify_otp(email, otp_code, dt)

# Get user information
user = get_user_by_email(email)
```

## 📊 Database Schema

### Tables
- **`coord_details`**: User coordinator information
- **`user_logs`**: Authentication and activity logs
- **`mail_logs`**: Email activity tracking

### Security Features
- **Password Hashing**: bcrypt with salt
- **Session Tokens**: Secure session management
- **Activity Logging**: Complete audit trail
- **OTP Expiry**: Time-based security

## 🔧 Configuration

### Timezone Support
- **IST Integration**: Indian Standard Time handling
- **UTC Conversion**: Automatic timezone conversion
- **Datetime Parsing**: Robust datetime handling

### Security Settings
- **OTP Expiry**: Configurable OTP validity period
- **Password Policies**: Secure password requirements
- **Session Timeout**: Automatic session cleanup

## 🛡️ Security

This module implements enterprise-grade security practices:

- **🔐 Password Protection**: bcrypt hashing with salt
- **📱 OTP Security**: Time-based one-time passwords
- **🕐 Session Management**: Secure session handling
- **📊 Activity Monitoring**: Complete audit logging
- **🧹 Automatic Cleanup**: Expired data removal

## 📈 Performance

- **Connection Pooling**: Efficient database connections
- **Lazy Loading**: On-demand client initialization
- **Optimized Queries**: Indexed database queries
- **Caching Strategy**: Smart data caching

---

<div align="center">

**Built with ❤️ for secure, scalable authentication**

*Part of the Lets Connect! AI Edition project*

</div>