# 🧩 Components

**Modular UI components for the Lets Connect! AI-powered recruitment platform**

---

## 🎯 Overview

The `components/` directory contains reusable Streamlit UI components that power the **Lets Connect!** application. Each component is designed to be self-contained, focused, and easily maintainable.

## 📦 Component Structure

```
components/
├── base_invitation.py     # 📝 Base message template editor
├── company_info.py        # 🏢 Company details & coordinator selection
├── generate_ainvite.py    # 🤖 AI-powered email generation
├── display_ainvite.py     # 📧 Email display, editing & sending
├── login_ui.py           # 🔐 Authentication & OTP verification
├── sidebar.py            # ⚙️ Settings panel & session stats
├── expander.py           # ℹ️ Help sections & FAQ
└── markdown.py           # 🎨 Shared markdown & styling utilities
```

## 🚀 Key Features

- **🎨 Modern UI/UX** - Clean, intuitive interface components
- **🔧 Modular Design** - Each component handles a specific responsibility
- **🔄 State Management** - Seamless Streamlit session state integration
- **📱 Responsive** - Works across different screen sizes
- **🎯 Focused** - Single responsibility principle

## 🛠️ Component Details

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `base_invitation.py` | Template editor | Customizable message templates |
| `company_info.py` | Data input | Company details & coordinator selection |
| `generate_ainvite.py` | AI processing | Mistral AI integration & generation |
| `display_ainvite.py` | Email handling | Display, edit, send & save functionality |
| `login_ui.py` | Authentication | OTP-based secure login system |
| `sidebar.py` | Settings | Session stats & quick settings |
| `expander.py` | Help system | FAQ, troubleshooting & guides |
| `markdown.py` | Utilities | Shared styling & markdown helpers |

## 🔌 Usage

Each component follows the same pattern:

```python
from components.component_name import render_component_function

# In your main app
render_component_function(parameters)
```

## 🎨 Design Principles

- **Consistency**: Uniform styling across all components
- **Accessibility**: Clear labels, proper contrast, semantic structure
- **Performance**: Efficient rendering with minimal state changes
- **Maintainability**: Clean, documented, and testable code

## 📋 Dependencies

- **Streamlit** - Core UI framework
- **Session State** - For component communication
- **External APIs** - Mistral AI, Gmail SMTP

---

**Built with ❤️ for seamless recruitment communications**