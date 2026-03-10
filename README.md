# TicTacToe Genetic AI & API

## 📌 Overview
This project implements an **artificial intelligence agent for a Tic‑Tac‑Toe game** using a genetic algorithm, and exposes a REST/Socket‑based API for managing player data and interacting with the trained model. It also includes benchmarking utilities and monitoring configuration for Prometheus/Grafana.

The workspace is split between the core game/AI code (`src/`) and supporting scripts such as training, benchmarking, and a Flask‑based web service.

---

## 🧱 Architecture & Components

### 🧠 Core AI Components (`src/`)
- **`brain.py`** – PyTorch neural network (`Brain`) representing the agent.
- **`genetic_algorithm.py`** – Implements `GeneticTrainer`: population initialization, evaluation, selection, crossover, mutation, and evolutionary loop.
- **`game_env.py`** – `TicTacToe` environment plus `check_winner` helper.
- **`player_wrappers.py`** – Utility players: random, heuristic, and wrappers to query the trained model. Includes threat detection and winning‑move logic.

### 🎮 Game & Training Scripts
- **`train.py`** – Entry point for running the genetic algorithm to evolve a model.
- **`benchmark.py`** – Play model against opponents, compute win/loss statistics.
- **`game.py`** – CLI to play human vs AI.
- **`pytorch_gpu.py`** – Helper to display available GPU info.
- **`main.py`** – Bootstrapper for API application (creates Flask app).

### 🌐 Web API (`src/app/`)
A Flask application exposing endpoints for player management and authentication:
- Config/dataclass definitions (`config.py`).
- Logging infrastructure using `loguru` (`logger_manager.py`).
- Database initialization (`db_manager.py`).
- Blueprints under `src/routes/` for login, token renewal, player CRUD, user operations.
- Models and schemas using SQLAlchemy and Marshmallow (`src/models/`).

### 📊 Monitoring (`monitoring/`)
- Grafana dashboard and datasource configuration.
- Prometheus configuration file for scraping metrics.

### 🛠 Utility & Helpers
- RBAC decorators and route helpers under `src/utils/`.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- `pip` or virtualenv
- (Optional) CUDA‑capable GPU for faster training
- PostgreSQL instance for the API (or adjust to another SQL DB)
- Docker if you plan to launch monitoring stack

### Installation
```bash
cd E2-E3_teston_niels-patrick
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the project root with the following variables:
```
DB_USERNAME=...
DB_PASSWORD=...
DB_NAME=...
DB_HOST=...
DB_PORT=5432
JWT_TOKEN_LOCATION=headers
JWT_HEADER_NAME=Authorization
JWT_HEADER_TYPE=Bearer
JWT_SECRET_KEY=your_secret
FERN_KEY=<base64 key from `Fernet.generate_key()`>
HOST=0.0.0.0
PORT=5000
```

### Training the Model
Run the genetic trainer to evolve a strong Tic‑Tac‑Toe policy:
```bash
python train.py  # edit parameters inside if needed
```
Learned weights are saved as a Torch tensor (see `best_ttt_model.pt`).

### Playing Against the AI
Use the CLI script:
```bash
python game.py
```
or play automated benchmarks:
```bash
python benchmark.py --model best_ttt_model.pt --opponent heuristic
```

### Starting the Web API
```bash
python main.py
```
The API will run on the host/port specified in `.env`. Swagger documentation is available at `http://<host>:<port>/apidocs/`.

### API Endpoints
| Path | Method | Description |
|------|--------|-------------|
| `/api/login` | POST | Authenticate user and receive JWT |
| `/api/token/refresh` | POST | Refresh access token |
| `/api/player/` | GET, POST, PUT | List/add/update players (JWT required for GET/PUT) |
| `/api/player/<id>` | GET | Retrieve single player (JWT required) |

The Swagger UI provides interactive docs.

### Monitoring
Launch Prometheus and Grafana (see `monitoring/` subfolders) to visualize metrics. The Grafana Dockerfile builds a custom image with pre‑provisioned dashboards and datasources.

---

## 📂 Repository Structure
```
benchmark.py          # benchmarking utilities
best_ttt_model.pt     # example trained weights
game.py               # CLI to play human vs AI
main.py               # entrypoint for Flask API
train.py              # script to run genetic training

src/                  # Python package containing core logic
 ├─ brain.py
 ├─ game_env.py
 ├─ genetic_algorithm.py
 ├─ player_wrappers.py
 ├─ app/              # flask application components
 ├─ models/           # ORM models and schemas
 ├─ routes/           # HTTP endpoints
 └─ utils/            # helper functions and decorators

monitoring/           # Prometheus/Grafana infrastructure
requirements.txt      # Python dependencies
README.md             # this document
```

---

## 🧪 Testing
No automated tests are included at the moment. Consider adding unit tests for core modules (e.g. game logic, genetic algorithm, API).

## 🔧 Development Tips
- Use `src/app/logger_manager.logger_manager` for consistent logging.
- The genetic algorithm prints progress; you can redirect output to a log file.
- To reset the Flask logger (useful in tests) call `LoggerManager.reset_instance()`.

## 📄 License
Add your license information here.

---

> _Happy hacking!_ 🎉
