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

## 📈 Monitoring & Metrics

This project includes real-time monitoring of AI performance using Prometheus and Grafana.

### What is Monitored?
- **AI win, loss, and draw rates** over the last 10 games (from the database, not just in-memory)
- **Retrain signal**: If the AI's loss rate exceeds a threshold, a metric signals that retraining is recommended
- **Game statistics**: Number of recent games with known outcomes

### How it Works
- The Flask API exposes a Prometheus-compatible metrics endpoint at:
  - `GET /api/monitoring/metrics`
- Prometheus scrapes this endpoint every 15 seconds (configurable)
- Metrics are computed from the last 10 games saved in the database
- Grafana dashboards visualize these metrics for live monitoring and alerting

### Setup Steps

1. **Setup prometheus.yml**
   - In folder /monitoring/prometheus, the prometheus.yml file must contain 2 jobs: one for prometheus itself, and another one for the API.
2. **Setup Grafana**
   - In /monitoring/grafana, Grafana must have its own Dockerfile, to copy provisioning files and expose the service on port 3000.
   - In the /provisioning subfolder, prepare the dashboards.yml file and the datasources.yml file, configured to get data from Prometheus every 5 seconds.
3. **Setup compose.yaml services**
   - postgres: The PostgreSQL service must be setup with the database name, user, password and port
   - e2-e3-tictactoe: The Flask API service. Must depend on the postgres service.
   - prometheus: The Prometheus service. Must listen on port 9090 and use the prometheus.yml file previously configured. Must depend on e2-e3-tictactoe.
   - grafana: The Grafana service. Must listen on port 3000 and use the Dockerfile previously set up in /monitoring/grafana. Must also use the /provisioning folder. Must depend on prometheus.
   - (optional) uptime-kuma: If you want to monitor the API health. You can set up the port to 3001. Must depend on e2-e3-tictactoe.

### User Access
Once the application, database and monitoring tools are deployed, all services started, the user can access the Grafana UI and check the model's metrics dashboard by following these steps:
   - Default: [http://localhost:3000](http://localhost:3000)
   - Login (default admin/admin), open the "AI Last 10 Games" dashboard
   - Pytest: In Alerting/Alert rules, edit the ttt_should_retrain_alert and in part 4 - Pending period, set it to 0 before starting the Pytest, then set it back to 15 minutes


### Key Metrics
- `ttt_ai_last_10_win_rate` – Win rate of the AI in the last 10 games
- `ttt_ai_last_10_loss_rate` – Loss rate of the AI in the last 10 games
- `ttt_ai_last_10_draw_rate` – Draw rate of the AI in the last 10 games
- `ttt_ai_last_10_known_games` – Number of recent games with a determinable outcome
- `ttt_ai_last_10_should_retrain` – 1 if loss rate exceeds threshold, else 0

### Troubleshooting
- If metrics do not update, check:
  - The Flask API logs for metric update info
  - Prometheus targets page (`/targets`) for scrape errors
  - Grafana dashboard time range (set to "Last 5 minutes" or similar)
- If you see duplicate series, use `max(metric) by ()` in Grafana queries

---

## 🧪 Running Tests

To run the test suite, make sure you have installed all dependencies and activated your virtual environment. Then, from the project root, run:

```bash
pytest
```

This will automatically discover and execute all tests in the `tests/` directory. You can also run a specific test file, for example:

```bash
pytest tests/test_07_ai_model.py
```

Some tests may require a configured database and a trained model file (e.g., `best_ttt_model.pt`).

If you want to see print output (such as model evaluation messages), use:

```bash
pytest -s
```

---

## 🔄 Model Delivery Chain: Retraining, Validation, and Deployment

### Installation & Setup
1. **Install dependencies and set up the environment** (see Installation and Configuration above).
2. **Start the API and monitoring stack** (see Starting the Web API and Monitoring sections).

### Usage: Model Retraining and Delivery
1. **Trigger Model Retraining**
   - Send a POST request to `/api/monitoring/retrain-model` with the desired parameters (requires Admin JWT):
     ```json
     {
       "populationSize": 100,
       "gamesPerEval": 60,
       "mutationRate": 0.05,
       "mutationStd": 0.15,
       "generations": 200
     }
     ```
   - The API will start the training process asynchronously. Only one training can run at a time.
   - You will receive a 202 Accepted response if training starts, 409 if already running, or 400 for missing/invalid data.

2. **Monitor Training Progress**
   - Poll the `/api/monitoring/training-status` endpoint to check if training is `running`, `finished`, or `error`.
   - When training is finished, fetch the result and report via `/api/monitoring/training-result`.
   - The response includes a message about the model quality and URLs to generated plots (e.g., win/loss/draw gauges, training evolution curve).
   - To display a plot, fetch `/api/monitoring/training-report/<filename>` using the provided URLs.

3. **Model Validation**
   - After training, the API evaluates the new model. If the loss rate is too high, the model is discarded and a message is returned. If the model is good, it is saved and the result is reported.
   - Visualizations (gauge plots and training curves) are generated and available for download or display in the frontend.

### Testing the Delivery Chain
- Use `pytest` to run the test suite and validate the retraining and monitoring endpoints:
  ```bash
  pytest
  ```
- The test `test_retrain_model_statuses` checks all retraining statuses (202, 400, 409) and ensures the training lock is properly handled.
- You can also manually trigger retraining and check the results and plots via the API and Grafana dashboards.

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
