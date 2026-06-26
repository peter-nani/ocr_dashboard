docker volume prune -f
docker-compose down --remove-orphans
docker-compose up --build -d


Here is a clean, comprehensive README.md report tailored for your project. It documents the architecture, the Docker infrastructure, the configuration mechanics, and the mobile-responsive user interface you have built.

AGNES // Telemetry Core & Social Activity Feed
AGNES is a mobile-first, high-performance telemetry dashboard built with FastAPI / Uvicorn and Bootstrap 5.3. It aggregates, processes, and presents real-time data queues and image extraction pools into a clean, modern social-media-style timeline (inspired by Instagram/Threads) optimized for instant mobile browsing and single-thumb scrolling on iOS and Android devices.

🛠 Project Architecture
The system consists of an automated processing pipeline that updates local directory pools on the host machine, which are seamlessly synchronized and served securely via a containerized web server.

+-------------------------------------------------------------+
|                        HOST MACHINE                         |
|                                                             |
|  /root/ocr_extraction/processed_history/   --> [Mounted] --+
|  /tmp/                                     --> [Mounted] --|
|  /root/trans/                              --> [Mounted] --|
+-------------------------------------------------------------+ |
                                                                v
                                              +-----------------------------------+
                                              |          DOCKER CONTAINER         |
                                              |        (dashboard_web_app)        |
                                              |                                   |
                                              |  +-----------------------------+  |
                                              |  |     FastAPI / Uvicorn       |  |
                                              |  |  (Reads pools, serves feed) |  |
                                              |  +-----------------------------+  |
                                              +-----------------------------------+
📦 Infrastructure Configuration (docker-compose.yml)
The application is fully containerized to isolate dependencies and guarantee environment consistency.

Volume Mapping Explanation
./app:/app: Binds the local application source directory. Enables hot-reloading code changes without rebuilding the container.

./data:/app/data: Persists critical runtime storage (e.g., SQLite dashboard.db, user registration sessions) across container restarts.

/root/ocr_extraction/processed_history:/data:ro: Grants the application read-only (:ro) access to historic pipeline outputs safely.

/tmp:/tmp: Shares the system temporary directory to monitor active/transient image queues.

/root/trans:/root/trans:ro: Maps localized structural transformation and translation images for matrix pool processing.

📱 Front-End Interface Design
The user interface shifts away from rigid administrative designs into a fluid, user-friendly activity timeline.

Interface Philosophy
Mobile-First Grid: Designed utilizing Bootstrap 5.3 framework layers to guarantee seamless layout responsiveness across Safari (iOS) and Chrome/WebView (Android).

Natural Typography: Drops stylized decorative fonts in favor of native device font stacks (-apple-system, SF Pro, Segoe UI, Roboto) to maximize screen readability and performance.

AMOLED Dark Mode: Employs a pure black background configuration (#000000) to maximize battery efficiency and visual contrast on modern mobile screens, alongside an alternate light mode.

Sticky HUD Controls: Implements a persistent blurred top header for navigation/filtering chips and a fixed bottom drawer housing active controls like theme configuration and live state-sync switches.

⚙️ Core Engine Features
Dynamic Pool Parsing: Loops dynamically over structural data channels (pools.json) and maps them directly to independent section nodes on your timeline.

Auto-Synchronization Engine: Includes an integrated JavaScript background worker executing automated network frame refetches every 10000ms (10 seconds) when toggled active.

Local State Persistence: Caches preferred client data metrics (active theme selections, interval sync flags) directly inside the client browser’s localStorage to retain configuration between visits.