import json

# Read the notebook
with open("assignment.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

# Create the pip install cell
pip_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Install required packages\n",
        "!pip install pandas numpy matplotlib scipy statsmodels scikit-learn joblib",
    ],
}

# Insert at the beginning (after the first markdown cell)
notebook["cells"].insert(1, pip_cell)

# Write back
with open("assignment.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("✅ Added pip install cell to notebook!")
