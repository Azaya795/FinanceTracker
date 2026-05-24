# 🚀 Quick Start Guide: How to Run and Push

This guide provides step-by-step instructions on setting up your environment, running the MVP application locally, and submitting your progress to GitLab for the **Software-Engineering-2026** course.

---

## 🛠️ 1. Local Environment Setup

### Step 1: Create a Virtual Environment
To keep your dependencies clean and isolated, initialize a Python virtual environment in your project root:
```powershell
python -m venv .venv
```

### Step 2: Install Project Requirements
If you receive a PowerShell security error when trying to run `.venv\Scripts\Activate.ps1`, you can **bypass the activation** completely and install your packages directly using:
```powershell
.venv\Scripts\pip install -r requirements.txt
```
*(Alternatively, temporarily bypass policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`, then run `.venv\Scripts\Activate.ps1`)*

### Step 3: Configure Your IDE (Remove Lint Errors)
If your editor shows a red warning under `import flask`:
1. Press **`Ctrl + Shift + P`** (or `F1` / `Cmd + Shift + P` on Mac) to open the Command Palette.
2. Search for and select **`Python: Select Interpreter`**.
3. Choose the option marked **`(.venv)`** (pointing to `.\.venv\Scripts\python.exe`).
4. The red import warnings will disappear instantly.

---

## 💻 2. How to Run the Application

Select one of the two methods below to run your application:

### Method A: Running with Docker (Recommended)
Use this method if you have **Docker Desktop** installed and running on your system:
```powershell
# Start the entire multi-container stack (Flask Web App + PostgreSQL)
docker-compose up --build
```
* **App URL:** [http://localhost:5000](http://localhost:5000)
* **Database:** Runs securely inside the containerized network (PostgreSQL).
* *To stop the containers: Press `Ctrl + C` in the terminal.*

### Method B: Running Standalone (Offline SQLite Fallback)
If Docker Desktop is offline or not installed, our robust fallback logic allows you to start developing immediately:
```powershell
.venv\Scripts\python app/app.py
```
* **App URL:** [http://localhost:5000](http://localhost:5000)
* **Database:** Gracefully falls back to a local relational SQLite database (`app.db`).

---

## 🧪 3. How to Run Unit Tests

To run the complete automated test suite and check code coverage (baseline is 75%, exceeding the 70% requirement):
```powershell
# Run the test suite and output coverage metrics
.venv\Scripts\python -m pytest --cov=app tests/
```

---

## 🚀 4. How to Push and Submit (Sprint 1 Milestone)

Follow these git commands to submit your project to the course group:

### Step 1: Add GitLab Remote URL
Add your private course repository as a remote (replace with your exact subgroup URL):
```powershell
git remote add origin https://gitlab.com/Software-Engineering-2026/your-subgroup/your-mvp-repo.git
```

### Step 2: Submit the Development Branch
According to the Git Workflow checklist, all code changes must be submitted on `develop` branch:
```powershell
# Create and switch to the develop branch (if not already on it)
git checkout -b develop

# Push the develop branch to GitLab
git push -u origin develop
```

### Step 3: Create and Submit the Sprint Tag
To mark your Sprint 1 submission, tag the commit and push it to trigger the automated CI/CD pipeline:
```powershell
# Tag the current baseline commit (already done for this template)
git tag v0.1-sprint1

# Push the tag to GitLab
git push origin v0.1-sprint1
```

Once pushed, check your GitLab Repository **CI/CD > Pipelines** page to verify your Docker build status!
