import pandas as pd
import os

file_path = r'C:\Users\Lenovo\Desktop\DAP391_project\07_audit_log\AI_Audit_Log.xlsx'
output_path = r'C:\Users\Lenovo\Desktop\DAP391_project\07_audit_log\AI_Audit_Log_Updated.xlsx'

data = [
    {
        "Evaluation criteria": "Final report document",
        "Descriptions": "Final Report (LaTeX & Slides): clear structure, figures/tables and references.",
        "Max. points": 20,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Help me write the Final Report in markdown, summarize the RFM analysis and Uplift Model results, and generate structure for presentation slides.'\nReflection: The AI provided a good baseline for the reports. I manually corrected model performance metrics (from baseline accuracy 0.9861 down to 0.7092) because the AI hallucinated the results prior to actual script execution."
    },
    {
        "Evaluation criteria": "Business Understanding, Data Collection, Preparation",
        "Descriptions": "Evaluate understanding of the problem context, data collection approach, and data preprocessing steps.",
        "Max. points": 5,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Act as a Business Analyst, brainstorm the problem statement for the Online Retail II dataset, define the RFM (Recency, Frequency, Monetary) approach, and write an ETL script.'\nReflection: AI correctly identified the 4 segments (Persuadables, Sure Things, Sleeping Dogs, Lost Causes). The ETL script successfully removed missing CustomerIDs and capped outliers at the 99th percentile before SQL Server insertion."
    },
    {
        "Evaluation criteria": "Data Analysis with Python",
        "Descriptions": "Assess the use of appropriate analytical techniques to derive meaningful insights from data.",
        "Max. points": 10,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Write Python code using pandas to calculate RFM scores based on the core.Transaction table. Explain the feature engineering choices for calculating the Base Tier from Recency and adding points for F and M.'\nReflection: AI explained the heuristic approach well but failed to account for chronological train-test splitting in analysis, which I had to fix manually to prevent data leakage."
    },
    {
        "Evaluation criteria": "Data Visualization in advanced",
        "Descriptions": "Evaluate the effectiveness and appropriateness of advanced visualizations in communicating insights.",
        "Max. points": 10,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Develop advanced Python-based visualization scripts utilizing matplotlib and seaborn to construct an uplift histogram, an RFM metric comparative chart, a Qini curve, and a cost-benefit matrix.'\nReflection: AI's code for visualizations was excellent. The Qini curve visualization accurately depicted the model's performance compared to random targeting."
    },
    {
        "Evaluation criteria": "Build model for prediction",
        "Descriptions": "Evaluate the selection and application of predictive models relevant to the project problem.",
        "Max. points": 15,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Implement and train a T-Learner uplift meta-model using the XGBoost framework. Compare performance with baseline models.'\nReflection: AI hallucinated the `XGBClassifierTLEarner` class from CausalML. I had to refactor the codebase to manually use two separate `xgboost.XGBClassifier` models for the control and treatment groups."
    },
    {
        "Evaluation criteria": "Integrating Services into an application",
        "Descriptions": "Assess integration of multiple AI services (AWS/GCP) into the application for intelligent Q&A and decision support.",
        "Max. points": 10,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Write a Flask REST API (app.py) with AWS deployment considerations, including endpoints to get the Uplift score of a specific customer and retrieve the top 20% Persuadables.'\nReflection: AI successfully generated the Flask API endpoints (/api/customer/<id> and /api/top_targets), providing a solid integration foundation for external apps."
    },
    {
        "Evaluation criteria": "Develop applications and AI powered solutions",
        "Descriptions": "Assess the design and implementation of applications integrating data analysis and AI components.",
        "Max. points": 10,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Develop an interactive Streamlit-based web application and Power BI dashboard incorporating what-if simulation sliders, dynamic ROI projections, and an individual customer lookup.'\nReflection: AI delivered the streamlit application and correctly guided the Power BI DAX calculations (Total Cost, Expected Revenue, ROI %). I manually fixed a UTF-8 encoding error during PowerShell execution."
    },
    {
        "Evaluation criteria": "Q&A",
        "Descriptions": "Evaluate students' understanding, justification of decisions, and responsible use of digital and AI tools.",
        "Max. points": 20,
        "AI Audit & Reflection (30% of Total Score)": "Prompt: 'Generate a list of 10 potential Q&A questions that examiners might ask about the Uplift modeling approach, the T-Learner, and the CausalML implementation challenges.'\nReflection: Using AI for Q&A preparation helped anticipate questions about why we chose Uplift Modeling over standard Churn prediction, and how we solved the dependency issues."
    }
]

df_new = pd.DataFrame(data)

# Read existing file to keep old sheets
try:
    xl = pd.ExcelFile(file_path)
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_new.to_excel(writer, sheet_name='AI Audit & Reflection', index=False)
        for sheet in xl.sheet_names:
            df_old = xl.parse(sheet)
            df_old.to_excel(writer, sheet_name=sheet, index=False)
    print(f"Successfully saved updated audit log to {output_path}")
except Exception as e:
    print(f"Error: {e}")
    # If it fails, just save the new one
    df_new.to_excel(output_path, sheet_name='AI Audit & Reflection', index=False)
    print(f"Saved only the new sheet to {output_path}")

