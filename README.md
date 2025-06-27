# AI Favs Backend

<div align="center">
  <h1>🤖 AI Favs</h1>
  <p>An intelligent content management system powered by AI</p>
  
  ![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
  ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
  ![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)
  ![License](https://img.shields.io/badge/License-MIT-yellow.svg)
</div>

## ✨ Features

- 🔗 **Smart Content Collection**: Automatically extract and process articles from WeChat Official Accounts
- 🤖 **AI-Powered Organization**: Auto-categorization and tagging using advanced language models
- 💬 **Intelligent Chat**: RAG-powered conversational interface for your collected content
- 🎙️ **Podcast Generation**: Convert articles to audio podcasts with TTS
- 🔍 **Vector Search**: Semantic search through your knowledge base
- 🏷️ **Smart Categorization**: Automatic content classification and tagging
- 📱 **RESTful API**: Complete REST API with OpenAPI documentation

## 🛠 Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLAlchemy with SQLite
- **AI/ML**: LangChain, OpenAI GPT, FAISS Vector Store
- **Background Tasks**: FastAPI BackgroundTasks
- **Web Scraping**: Playwright
- **Audio Processing**: Pydub, TTS
- **Containerization**: Docker & Docker Compose
- **Database Migration**: Alembic

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Docker & Docker Compose (optional)
- OpenAI API Key

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone https://github.com/your-username/ai-favs-backend.git
cd ai-favs-backend
```

2. **Install Poetry** (if not already installed)
```bash
# Via pipx (recommended)
pipx install poetry

# Via Homebrew (macOS)
brew install poetry
```

3. **Install dependencies**
```bash
poetry install
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

5. **Run the application**
```bash
# Using poetry
poetry run uvicorn app.server:app --reload

# Or using langchain serve
poetry run langchain serve
```

6. **Access the application**
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

### Option 2: Docker Deployment (Recommended)

1. **Clone and configure**
```bash
git clone https://github.com/your-username/ai-favs-backend.git
cd ai-favs-backend
cp .env.example .env
# Edit .env with your configuration
```

2. **Deploy with Docker Compose**
```bash
docker-compose up -d
```

3. **Access the application**
- API: http://localhost:8080
- Interactive API docs: http://localhost:8080/docs

## 📁 Project Structure

```
ai-favs-backend/
├── app/
│   ├── apis/                    # API routes and endpoints
│   │   ├── assistant/          # AI assistant functionality
│   │   ├── chat/               # Chat and conversation handling
│   │   ├── collection/         # Content collection management
│   │   ├── podcast/            # Podcast generation
│   │   └── user/               # User management
│   ├── db/                     # Database models and configuration
│   ├── utils/                  # Utility functions (LLM, vectorstore, etc.)
│   └── server.py               # FastAPI application entry point
├── migrations/                 # Database migrations
├── demo/                       # Demo scripts and examples
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image configuration
└── pyproject.toml             # Python dependencies and configuration
```

## 🔧 Configuration

Create a `.env` file in the project root with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./app/db/files/ai_favs.db

# Application Settings
DEBUG=True
PORT=8000

# Optional: LangSmith for monitoring
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
```

## 📚 API Documentation

### Core Endpoints

- **Collections**
  - `POST /collection/add` - Add new content to collection
  - `GET /collection/list/get` - Retrieve collections with filtering
  - `GET /collection/overview` - Get collections overview with categories

- **Chat**
  - `POST /chat` - Send chat messages with RAG
  - `POST /chat/stream` - Streaming chat responses
  - `GET /chat/followups/get` - Get suggested follow-up questions

- **Assistant**
  - `POST /assistant/query` - Query the AI assistant

- **Podcasts**
  - `POST /podcast/generate` - Generate podcast from content
  - `GET /podcast/list` - List user podcasts

### Interactive API Documentation

Visit `/docs` endpoint for comprehensive interactive API documentation powered by Swagger UI.

## 🔍 Key Features Explained

### Smart Content Processing
The system automatically processes WeChat articles by:
1. Extracting content using Playwright web scraping
2. Generating AI-powered summaries
3. Auto-categorizing content based on existing categories
4. Creating relevant tags using NLP
5. Storing content in vector database for semantic search

### RAG-Powered Chat
- Semantic search through your collected content
- Context-aware responses using your knowledge base
- Support for chat history and follow-up questions
- Streaming responses for real-time interaction

### Podcast Generation
Convert your articles into audio format:
- Text-to-speech conversion
- Background processing for large content
- Audio file management and serving

## 🚢 Deployment

### Production Deployment

1. **Using Docker Compose** (Recommended)
```bash
# Production configuration
docker-compose -f docker-compose.prod.yml up -d
```

2. **Manual Deployment**
```bash
# Build and run
docker build -t ai-favs .
docker run -p 8080:8080 --env-file .env ai-favs
```

### Health Checks

The application includes health check endpoints:
- Container health check via wget
- API health monitoring
- Database connection validation

## 📊 Database Schema

The application uses SQLAlchemy with the following main models:
- **User**: User management
- **Collection**: Content storage and metadata
- **Category**: Auto-generated content categories
- **Tag**: Content tagging system
- **Podcast**: Generated audio content

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure Docker builds successfully

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- 📫 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/ai-favs-backend/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/ai-favs-backend/discussions)

## 🔮 Roadmap

- [ ] Support for more content sources (YouTube, Medium, etc.)
- [ ] Advanced AI agents with tool usage
- [ ] Multi-language support
- [ ] Enhanced search capabilities
- [ ] Mobile app integration
- [ ] Collaboration features

---

<div align="center">
  <p>Built with ❤️ using FastAPI and LangChain</p>
</div>