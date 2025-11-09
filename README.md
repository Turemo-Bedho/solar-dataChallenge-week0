# Solar Challenge Week 0
**Cross-Country Solar Farm Analysis for Benin, Sierra Leone & Togo**  


## Project Overview
This project analyzes solar farm data from Benin, Sierra Leone, and Togo to identify high-potential regions for solar installation for MoonLight Energy Solutions.
This repository contains the complete solution for 10 Academy's Week 0 challenge, performing comparative analysis of solar irradiance data across three West African countries. Key deliverables include:
- Automated data cleaning pipelines
- Country-specific EDA notebooks
- Statistical comparison framework
- Visualization


## Setup Instructions

### Prerequisites
- **Python 3.11+**
- **Git**

---

###  Installation

#### 1. Clone the repository
```bash
git clone https://github.com/Turemo-Bedho/solar-dataChallenge-week0.git
cd solar-dataChallenge-week0
````

---

#### 2. Create and activate a virtual environment

Using **venv** (recommended):

```bash
# Create virtual environment
python -m venv venv
```

**Activate it:**

* On **Windows**:

  ```bash
  venv\Scripts\activate
  ```

* On **macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

---

#### 3. Install dependencies

Once the environment is active, run:

```bash
pip install -r requirements.txt
```

---

✅ **Tip:** You can confirm your environment is active if your terminal prompt shows `(venv)` at the beginning.

````
````

## 📂 Repository Structure
```
solar-dataChallenge-week0/
├── data/                   # Raw and cleaned datasets (gitignored)
├── notebooks/
│   ├── benin_eda.ipynb     # Complete Benin analysis
│   ├── sierraleone_eda.ipynb
│   └── togo_eda.ipynb
├── src/                    # Python modules
├── .github/workflows/      # CI/CD pipelines
│   └── ci.yml              
├── requirements.txt        # Dependency list
└── README.md               # This document
```


## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.