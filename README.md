# Biomed Chat

> A cutting-edge AI-powered chatbot interface designed specifically for biomedical engineers with modern UI/UX and professional design.

## Project Overview

Biomed Chat is a specialized chatbot interface tailored for biomedical engineers, featuring a stunning modern design with glass morphism effects, smooth animations, and an intuitive user experience. The application proxies to multiple AI providers including Grok, Gemini, OpenAI, and Anthropic, with RAG capabilities and a tailored system prompt that assumes baseline field expertise.

**Note on API Providers:** This project is built around the Grok API, which has demonstrated high performance on benchmarks. While other providers are supported, Grok is recommended for the best experience.

## Features

### 🎨 Modern UI/UX Design
- **Dynamic Animated Background**: Beautiful gradient background with floating orbs and smooth color transitions
- **Glass Morphism Effects**: Modern glass-like components with backdrop blur and transparency
- **Gradient Text Effects**: Eye-catching gradient text for branding and headings
- **Advanced Animations**: Smooth 60fps animations and micro-interactions throughout
- **Responsive Design**: Optimized for all screen sizes with mobile-first approach
- **Accessibility**: High contrast support, reduced motion preferences, and keyboard navigation

### 🚀 User Experience
- **Intuitive Navigation**: Enhanced navbar with hover effects and active state indicators
- **Modern Chat Interface**: Glass morphism message bubbles with smooth slide-in animations
- **Enhanced Settings Page**: Professional settings interface with animated cards and modern controls
- **Interactive Elements**: Subtle hover animations, loading states, and visual feedback
- **Modern Form Controls**: Custom-styled inputs, switches, and buttons with glass effects

### 🤖 AI Capabilities
- **Multi-API Support**: Supports Grok, Gemini, OpenAI, and Anthropic APIs
- **Smart API Fallback**: Automatically uses mock responses when API key is not available
- **Biomedical Focus**: Specialized responses for biomedical engineering topics
- **Streaming Responses**: Real-time response streaming for better user experience
- **Mock Mode**: Realistic demonstration responses when API is unavailable

## Setup

### Prerequisites
- Node.js 18 or higher
- Python 3.8+ (for backend dependencies)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/teddytennant/biomed-chat.git
   cd biomed-chat
   ```

2. **Install dependencies:**
   ```bash
   npm install
   pip install -r requirements.txt
   ```

## Configuration

1. **Create environment file:**
   Create a `.env` file in the root directory with the following configuration:

   ```env
   # Required: Set the API provider
   API_PROVIDER="grok"  # Options: "grok", "gemini", "openai", or "anthropic"
   
   # Required: API key for your chosen provider (only one needed)
   GROK_API_KEY="your_grok_api_key_here"
   # GEMINI_API_KEY="your_gemini_api_key_here"
   # OPENAI_API_KEY="your_openai_api_key_here"
   # ANTHROPIC_API_KEY="your_anthropic_api_key_here"
   
   # Optional: Additional configuration
   # XAI_MODEL=grok-4
   # PORT=3000
   # SITE_PASSWORD=your_password_here
   ```

2. **For mock/demo mode:**
   Comment out or remove the API key to enable mock responses:
   ```env
   API_PROVIDER="grok"
   # GROK_API_KEY="your_grok_api_key_here"  # Commented out for mock mode
   ```

## Usage

### Starting the Application

1. **Development mode:**
   ```bash
   npm run dev
   ```

2. **Production mode:**
   ```bash
   npm run build
   npm start
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000` to access the application.

### Example Commands

Once the application is running, you can interact with the AI assistant using biomedical engineering queries:

- "Explain the biomechanics of knee joint replacement"
- "What are the latest developments in neural prosthetics?"
- "Design considerations for biocompatible materials"
- "How do cardiac pacemakers regulate heart rhythm?"

## API Providers

The application supports multiple AI providers with easy switching:

### Supported Providers
- **Grok (xAI)** - Recommended for best performance
- **Gemini (Google)** - Good for technical discussions
- **OpenAI** - Reliable general-purpose AI
- **Anthropic (Claude)** - Strong reasoning capabilities

### Provider Configuration
Set your preferred provider in the `.env` file:
```env
API_PROVIDER="grok"  # Change to your preferred provider
```

Only the API key for your chosen provider is required.

## Mock Mode

When no API key is configured for the selected provider, the system automatically provides realistic mock responses for demonstration purposes. This allows you to:

- Test the user interface without API costs
- Demonstrate functionality to stakeholders
- Develop and debug without external dependencies
- Experience the full application flow

Mock responses are specifically tailored to biomedical engineering topics and maintain the same format as real AI responses.

## Contributing

We welcome contributions to improve Biomed Chat! Here's how to get started:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature/your-feature-name`
6. Submit a pull request

### Guidelines
- Follow the existing code style and conventions
- Add tests for new features
- Update documentation as needed
- Ensure responsive design principles are maintained
- Test across different browsers and devices

### Reporting Issues
Please use the GitHub Issues tab to report bugs or request features. Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for the biomedical engineering community**
