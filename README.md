# Phishing Email Detection System and Analysis using Natural Language Processing

## Project Overview
A system designed to detect phishing emails using Natural Language Processing (NLP) and advanced machine learning models, improving email security and combating cyber threats.

---

## Features
- **Phishing Detection:** Classifies emails as phishing or legitimate using the Llama3 model.
- **Dashboard Visualization:** Real-time data insights with Grafana.
- **Web Application:** Interactive interface for managing and detecting phishing emails:
  - **Frontend:** Built with Next.js, TypeScript, and Tailwind CSS.
  - **Backend:** Powered by Python and FastAPI.
- **Public Resources:**
  - **Grafana Dashboard:** http://34.41.68.246:3000/public-dashboards/9b2ad83572b04d25a41d6217f6037673
  - **Frontend Deployment:** https://senior-project-48wy3dpyu-tons-projects-042d155b.vercel.app/

---

## Technologies Used
- **NLP Frameworks:** Llama3 for phishing detection.
- **Visualization Tools:** Grafana for dashboard insights.
- **Frontend:** Next.js, TypeScript, Tailwind CSS.
- **Backend:** FastAPI (Python).
- **Other Tools:**
  - `scikit-learn` for supplementary ML models
  - `matplotlib` and `seaborn` for data visualization

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/phishing-email-detection.git
   ```
2. Navigate to the project directory:
   ```bash
   cd phishing-email-detection
   ```
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Train Model:**
   Train the Llama3-based phishing detection model:
   ```bash
   python train_model.py
   ```

2. **Run Web Application:**
   Launch the Next.js frontend and FastAPI backend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   For the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

3. **View Dashboard:**
   Access the Grafana dashboard for insights:
   [http://34.41.68.246:3000/public-dashboards/9b2ad83572b04d25a41d6217f6037673](http://34.41.68.246:3000/public-dashboards/9b2ad83572b04d25a41d6217f6037673)

4. **Deploy:**
   Utilize provided scripts for cloud deployment.

---

## Contribution Guidelines
We welcome contributions to improve this project. Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments
Special thanks to the open-source community and the authors of referenced libraries and datasets for their valuable contributions.

