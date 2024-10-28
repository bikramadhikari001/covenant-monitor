# Covenant Monitor

An AI-powered financial covenant monitoring system that uses GPT-4 to analyze loan documents and track compliance.

## Features

- AI-powered document analysis using GPT-4
- Automatic covenant extraction and monitoring
- Real-time compliance tracking
- Intelligent alerts with GPT analysis
- Interactive dashboards
- Multi-user support

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd covenant-monitor
```

2. Create a .env file with your OpenAI API key:
```bash
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4
```

3. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

4. Start the application:
```bash
chmod +x run.sh
./run.sh
```

## Testing

Run the test suite:
```bash
python -m unittest test_app.py
```

## Usage

1. Upload a loan document through the web interface
2. GPT-4 will automatically extract covenants and requirements
3. Monitor compliance through the interactive dashboard
4. Receive AI-powered alerts and analysis for potential breaches

## Architecture

- Frontend: HTML, CSS, JavaScript
- Backend: Flask, SQLAlchemy
- AI: OpenAI GPT-4
- Database: SQLite (configurable)

## API Endpoints

- `/upload`: Upload and process loan documents
- `/dashboard`: View covenant monitoring dashboard
- `/api/alerts/analyze/<id>`: Get GPT analysis of alerts
- `/api/dashboard/summary`: Get compliance summary
- `/api/dashboard/trends`: Get compliance trends

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License
