# 🤝 Lets Connect! - AI Edition

<div align="center">

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://letsconnect-jumca2026.streamlit.app/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Mistral AI](https://img.shields.io/badge/AI-Mistral-ff6b6b.svg)](https://mistral.ai/)

**🚀 AI-Powered Campus Recruitment Email Generator**

*Generate personalized, professional recruitment invitation emails with the power of AI*

[🌐 **Live Demo**](https://letsconnect-jumca2026.streamlit.app/) | [📋 **Documentation**](#documentation) | [🚀 **Quick Start**](#quick-start)

</div>

---

## ✨ Features

### 🤖 **AI-Powered Personalization**
- **Smart Content Generation**: Each email is uniquely crafted for the target company using Mistral AI
- **Industry-Specific Tailoring**: Skills and messaging automatically adapted to company's domain
- **Context-Aware Writing**: Utilizes additional company information for better personalization
- **Multiple Variations**: Generate different versions of the same invitation

### 📧 **Professional Email Management**
- **Direct Email Sending**: Send emails directly from the application using Gmail integration
- **One-Click Copying**: Copy generated content to clipboard instantly
- **Draft Management**: Save and download email drafts with timestamps
- **Template Customization**: Modify base templates according to your needs

### 👥 **Multi-Coordinator Support**
- **Flexible Coordination**: Support for multiple placement coordinators
- **Dynamic Contact Information**: Automatically populate coordinator details
- **Configurable Signatures**: Professional email signatures with contact information

### 🎯 **Smart Configuration**
- **Adjustable Skill Points**: Choose between 4-7 bullet points highlighting student expertise
- **Real-time Preview**: See generated emails before sending
- **Session Tracking**: Monitor email generation statistics
- **Error Handling**: Robust fallback mechanisms ensure reliability

---

## 🚀 Quick Start

### 🌐 **Try It Online**
👉 **[Launch Application](https://letsconnect-jumca2026.streamlit.app/)**

### 💻 **Local Development**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/letsconnect-ai.git
   cd letsconnect-ai
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Open in Browser**
   Navigate to `http://localhost:8501`

---

## 📋 How to Use

### Step 1: **Base Message Configuration**
- Customize the template message that will be sent to companies
- Use placeholders like `{company_name}`, `{name}`, `{contact}` for personalization

### Step 2: **Company Information**
- Enter the target company name
- Select the appropriate placement coordinator
- Add specific company context (industry, hiring needs, etc.)
- Choose the number of skill bullet points (4-7)

### Step 3: **AI Generation**
- Click "🤖 Generate Personalized Invitation Mail"
- AI analyzes company information and generates tailored content
- Review the generated email for accuracy and relevance

### Step 4: **Send or Save**
- **Send Email**: Direct email sending with Gmail integration
- **Copy Content**: One-click clipboard copying
- **Save Draft**: Download as text file for future reference

---

## 🔧 Configuration

### 📁 **File Structure**
```
letsconnect-ai/
├── app.py                      # Main Streamlit application
├── data.json                   # Coordinator information and templates
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (create this)
├── components/                # UI components
│   ├── base_invitation.py     # Base message configuration
│   ├── company_info.py        # Company information form
│   ├── generate_ainvite.py    # AI generation logic
│   ├── display_ainvite.py     # Email display and actions
│   ├── sidebar.py             # Sidebar with settings
│   ├── expander.py            # Expandable help sections
│   └── markdown.py            # Markdown utilities
└── utils/                     # Utility functions
    ├── data_loader.py         # JSON data loading
    ├── openrouter_client.py   # AI client initialization
    ├── email_sender.py        # Email sending functionality
    ├── prompt_generator.py    # AI prompt creation
    └── post_processor.py      # Email post-processing
```

### ⚙️ **Configuration Files**

**`data.json`** - Coordinator information:
```json
{
  "coordinators": [
    {
      "name": "Coordinator Name",
      "email": "coordinator@university.edu",
      "phone": "+91 XXXXX XXXXX"
    }
  ],
  "base_message": "Your base email template..."
}
```

**`.env`** - Environment variables:
```env
OPENROUTER_API_KEY=your_api_key_here
```

---

## 🎨 Features Showcase

### 🤖 **AI Capabilities**
- **Mistral AI Integration**: Powered by state-of-the-art language models
- **Two-Stage Processing**: Initial generation + validation for quality assurance
- **Fallback Mechanism**: Ensures professional emails even if AI services are unavailable
- **Context Analysis**: Understands company industry and tailors content accordingly

### 📊 **Analytics & Tracking**
- **Session Statistics**: Track emails generated per session
- **Success Monitoring**: Monitor email sending success rates
- **Usage Insights**: Understand application usage patterns

### 🔒 **Security & Privacy**
- **Secure API Keys**: Environment-based configuration
- **No Data Retention**: Real-time processing without permanent storage
- **Gmail App Passwords**: Secure email authentication
- **Privacy-First**: No sensitive data stored permanently

---

## 🛠 Technical Details

### **Tech Stack**
- **Frontend**: Streamlit (Python web framework)
- **AI Engine**: Mistral AI via OpenRouter API
- **Email Service**: Gmail SMTP
- **Data Format**: JSON configuration files
- **Deployment**: Streamlit Cloud

### **Key Dependencies**
- `streamlit`: Web application framework
- `openai`: OpenRouter API client
- `python-dotenv`: Environment variable management

### **AI Model**
- **Model**: `mistralai/mistral-small-3.2-24b-instruct:free`
- **Temperature**: 0.7 (generation) / 0.2 (validation)
- **Max Tokens**: 800
- **Processing**: Two-stage generation with validation

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Your Changes**
4. **Commit Your Changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the Branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### 🐛 **Bug Reports**
Found a bug? Please open an issue with:
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

---

## 📖 Documentation

### **Environment Setup**
1. **OpenRouter API Key**: Get your free API key from [OpenRouter](https://openrouter.ai/)
2. **Gmail Configuration**: Enable 2FA and generate app-specific passwords
3. **Data Configuration**: Update `data.json` with your coordinator information

### **Customization**
- **Email Templates**: Modify base templates in `data.json`
- **UI Components**: Update components in the `components/` directory
- **AI Prompts**: Customize prompts in `utils/prompt_generator.py`

### **Deployment**
The application is deployed on Streamlit Cloud and automatically updates from the main branch.

---

## 🎯 About

**Lets Connect! - AI Edition** is developed by the **JUMCA Placement 2024-26** team at **Jadavpur University** to streamline campus recruitment communications. The application leverages artificial intelligence to generate personalized, professional invitation emails that effectively communicate the university's value proposition to potential recruiting companies.

### **Key Benefits**
- ⏱️ **Time Saving**: Generate emails in seconds instead of hours
- 🎯 **Personalization**: Each email is tailored to the specific company
- 📈 **Consistency**: Maintain professional standards across all communications
- 🤖 **AI-Powered**: Leverage cutting-edge AI for content generation
- 📊 **Scalable**: Handle multiple companies and coordinators efficiently

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Jadavpur University MCA Department** for institutional support
- **Mistral AI** for providing the AI capabilities
- **Streamlit** for the amazing web framework
- **OpenRouter** for API access and infrastructure

---

<div align="center">

**Made with ❤️ by JUMCA Placement 2024-26**

[🌐 **Live Application**](https://letsconnect-jumca2026.streamlit.app/) | [📧 **Contact**](mailto:officer.placement@jadavpuruniversity.in)

</div>