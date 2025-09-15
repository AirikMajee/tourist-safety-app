# 🛡️ Tourist Safety App (MVP)

## 🌍 Overview

The **Tourist Safety App** is an end-to-end platform that enhances **traveler safety** using:

* 🗺️ **Interactive Risk Maps** — visualize natural disaster zones, crime heatmaps, and restricted areas.
* 🚦 **Geo-fencing Alerts** — real-time notifications when entering high-risk zones.
* 🆔 **Digital Tourist ID (DTID)** — blockchain-backed digital identity for secure tourist registration.
* 🚨 **SOS & Emergency Response** — panic button with nearest police, hospital, and shelter details.
* 📢 **Advisory & Crowd Reporting** — official advisories + verified tourist reports.
* 📊 **Authority Dashboard** — admin view for monitoring incidents and approving reports.

This project is designed as a **hackathon MVP** but structured for future scalability.

---

## ✨ Features

### 👤 Tourist Features

* Register with a **Digital Tourist ID** (issued as an ERC-721 NFT on Polygon Amoy).
* View **safe vs risky routes** when planning travel.
* Get **safety scores (0–100)** with explanations.
* Receive **real-time alerts** when approaching hazard zones.
* Trigger **SOS** with one tap to notify nearest authorities.

### 🛂 Authority Features

* Admin dashboard to:

  * Approve or reject crowd reports.
  * Push official advisories.
  * Monitor live risk zones.
* Verify reports using **DTID signatures**.

---

## 🏗️ Tech Stack

### Frontend

* **Next.js (React)** + **TailwindCSS**
* **Leaflet** (OpenStreetMap tiles) for maps
* **shadcn/ui** for UI components

### Backend

* **Python (FastAPI)** or **Flask** (depending on setup)
* **PostgreSQL + PostGIS** for geo-data (optional in MVP)
* REST API for reports, advisories, safety scores

### Blockchain

* **Polygon Amoy Testnet**
* ERC-721 **Digital Tourist ID** smart contract (Solidity)
* Deployment & interaction via **Hardhat + ethers.js**

---

## 📂 Project Structure

```
tourist-safety-app/
│
├── backend/              # Python backend
│   ├── server.py         # Main server file (APIs)
│   ├── requirements.txt  # Python dependencies
│   └── tests/            # Backend tests
│
├── frontend/             # Next.js frontend
│   ├── pages/            # Routes (Next.js)
│   ├── components/       # UI components
│   └── package.json      # Frontend deps
│
├── contracts/            # Solidity smart contracts
│   ├── TouristID.sol     # ERC-721 DTID contract
│   └── hardhat.config.ts # Hardhat config
│
├── README.md             # Project documentation
├── .gitignore            # Ignore secrets, build, env files
└── .env / .env.local     # Local secrets (not committed)
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone Repo

```bash
git clone https://github.com/<your-username>/tourist-safety-app.git
cd tourist-safety-app
```

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run backend
uvicorn server:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`

### 3️⃣ Frontend Setup

```bash
cd frontend
yarn install   # or npm install
yarn dev       # or npm run dev
```

Frontend runs at: `http://localhost:3000`

### 4️⃣ Smart Contract Deployment

```bash
cd contracts
npm install
npx hardhat compile
npx hardhat run scripts/deploy.ts --network amoy
```

Update `DTID_CONTRACT` address in `.env`.

---

## 🔑 Environment Variables

**`backend/.env`**

```
PORT=8000
PUBLIC_BASE_URL=http://localhost:8000

# Blockchain
ALCHEMY_API_KEY=<your-alchemy-key>
AMOY_RPC=https://polygon-amoy.g.alchemy.com/v2/${ALCHEMY_API_KEY}
DEPLOYER_PRIVATE_KEY=0x<your-private-key>
DTID_CONTRACT=0x<deployed-contract-address>
```

**`frontend/.env.local`**

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
NEXT_PUBLIC_MAP_TILES=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

---

## 🚀 Usage (Demo Flow)

1. **Issue Tourist ID** (admin view) → NFT minted on Polygon Amoy.
2. **Tourist login** → sees interactive risk map.
3. **Route planning** → shows “Fastest vs Safest” route.
4. **Enter hazard zone** → triggers geofence alert.
5. **Press Panic Button** → SOS sent + nearest POIs listed.
6. **Admin dashboard** → shows reports, advisories, and ID-verified submissions.

---

## 🧪 Tests

### Backend

```bash
pytest -q
```

### Frontend

```bash
cd frontend
yarn test
```

### Smart Contract

```bash
cd contracts
npx hardhat test
```

---

## 📊 Roadmap

* [x] MVP: Risk map, DTID issuance, geofencing alerts, SOS
* [ ] Multi-language support (English, Hindi, Odia)
* [ ] AI anomaly detection (GPT integration)
* [ ] Full PostGIS backend for large datasets
* [ ] Production deployment (Docker + CI/CD)

---

## ⚠️ Security & Ethics

* **Do not push `.env` or private keys** to GitHub.
* DTID system is **demo-only**; for real use, must comply with govt KYC/immigration laws.
* Anomaly detection AI is **advisory only**; human authority verification required.

---

## 📜 License

MIT License © 2025 \ Airik Majee

---

👉 Do you want me to also generate a **short “Hackathon README” version** (one-pager with screenshots + demo steps), so you can paste that into your PPT repo link for judges?
