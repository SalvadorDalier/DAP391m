# RESEARCH PROPOSAL / THUYẾT MINH ĐỀ CƯƠNG NGHIÊN CỨU

| | |
| :--- | :--- |
| **Research Title / Tên đề tài** | Precision Coupon Marketing in Online Retail: A Causal Inference Approach using T-Learner XGBoost and RFM Feature Engineering |
| **Mentor / Giảng viên hướng dẫn** | Dr. Nguyen Van A |
| **Members / Nhóm sinh viên thực hiện** | 1. Thu Le (thulvm@fpt.edu.vn)<br>2. Nhu Nguyen (nhunqk@fpt.edu.vn)<br>3. Duc Dat (datddse180784@fpt.edu.vn)<br>4. Ngoc Minh (minhtn1412@gmail.com) |
| **Abstract / Tóm tắt đề tài** | Traditional mass coupon marketing strategies lead to high budget waste by targeting customers indiscriminately. This research proposes a precision coupon marketing system utilizing causal machine learning (T-Learner XGBoost meta-learner) integrated with RFM (Recency, Frequency, Monetary) feature engineering on the Online Retail II dataset. The system estimates the Conditional Average Treatment Effect (CATE) to classify customers into four actionable marketing segments: Persuadables, Sure Things, Sleeping Dogs, and Lost Causes. We implement the pipeline through a Flask REST API for real-time customer scoring and an interactive Streamlit dashboard featuring What-If simulations for marketing decision-support. Our model achieves an Area Under the Uplift Curve (AUUC) of 0.8830, significantly outperforming random targeting. |

**Keywords**: Uplift Modeling, T-Learner, XGBoost, RFM Analysis, Precision Marketing, Causal Inference, Online Retail II.

---

## 1. Introduction / Giới thiệu

### 1.1. Literature Review / Tình hình nghiên cứu trong và ngoài nước
International research on retail promotion has transitioned from heuristic segmentation to advanced predictive models. Historically, RFM (Recency, Frequency, Monetary) analytics introduced by Hughes (1994) served as the foundation for direct marketing. Over the last decade, researchers have focused on causal machine learning models rather than standard predictive classification. Künzel et al. (2019) formalized meta-learner architectures (S-Learner, T-Learner, X-Learner) for estimating the Conditional Average Treatment Effect (CATE). The T-Learner uses separate models for control and treatment groups, proving optimal when the response surfaces of the two groups differ significantly, a common trait in promotion campaigns.

In Vietnam, the explosive growth of e-commerce has triggered massive marketing spend. However, domestic studies still rely heavily on traditional RFM clustering or simple churn models. Practical applications of uplift modeling in Vietnamese retail remain scarce, resulting in inefficient "mass mailing" discount strategies that erode profit margins. Our proposed study bridges this gap by applying a localized, highly scalable T-Learner XGBoost framework to raw transactional data.

### 1.2. The Limitation of Current Works / Những hạn chế của các nghiên cứu hiện tại
Standard machine learning models predict overall purchase probability, which confounds baseline purchase propensity with promotional sensitivity. As a result, they target "Sure Things" (customers who would buy anyway) and miss "Persuadables" (who only buy due to the coupon), wasting marketing budget. Furthermore, modern causal inference libraries like CausalML are difficult to compile on standard Windows platforms due to complex C++ dependencies. Finally, existing analytical tools lack integrated what-if simulation capabilities that marketing managers can use to interactively test campaign budgets and ROI before launch.

### 1.3. The Necessity of the Research / Sự cần thiết tiến hành nghiên cứu
This research is necessary to develop a lightweight, self-contained causal inference framework that operates on standard computational environments. By manually structuring a T-Learner meta-model using separate XGBoost models, we circumvent compilation bottlenecks while retaining state-of-the-art causal predictive power. Scientifically, it contributes a detailed evaluation of Qini curves and Area Under the Uplift Curve (AUUC) metrics on large-scale transaction datasets. Practically, it delivers a direct mapping from continuous CATE values to operational customer segments, providing marketers with a transparent web dashboard to optimize campaigns.

---

## 2. Research Objectives / Mục tiêu của đề tài
* **Objective 1**: Design an ETL pipeline that cleans raw e-commerce data, handles outliers via 99th percentile capping, and structures data in SQL Server.
* **Objective 2**: Develop a custom T-Learner meta-model using dual XGBoost classifiers to calculate CATE for individual customers.
* **Objective 3**: Implement a Qini curve evaluation model to measure campaign performance against random targeting.
* **Objective 4**: Build a REST API for real-time customer CATE scoring and an interactive Streamlit dashboard for What-If business simulations.

---

## 3. Research Scope / Phạm vi nghiên cứu
The research covers transactions from the Online Retail II dataset (2009–2011) from the UCI Machine Learning Repository. Coupon issuance and redemption behavior are simulated to model treatment scenarios. The technology stack is limited to python-based data science packages (pandas, scikit-learn, xgboost, SQLAlchemy), a Flask web server, and a Streamlit dashboard.

---

## 4. Feasibility of Research / Tính khả thi của đề tài
The project has high feasibility as the database schemas, ETL scripts, and machine learning models are already fully implemented. The manual T-Learner achieved an AUUC of 0.8830 on test data, and both the Flask API and Streamlit what-if interfaces have been successfully tested. The system runs on basic computer hardware, eliminating the need for expensive high-performance computing clusters.

---

## 5. Approach and Method / Cách tiếp cận và phương pháp nghiên cứu
The system follows a modular software engineering approach combined with experimental machine learning validation. The database layer maps customers and invoices to SQL tables. Feature engineering derives Recency, Frequency, and Monetary scores. In the modeling phase, control and treatment groups are split. The control XGBoost model fits on base responses while the treatment model fits on treated responses. The CATE is predicted as the difference in probabilities. Evaluation is performed using the Qini curve. Finally, business integration is delivered via Streamlit tabs that calculate net profit projections based on coupon cost inputs.

---

## 6. Research Plan / Kế hoạch thực hiện nghiên cứu

| No. | Date / Thời gian | Task / Nhiệm vụ | Expected Output / Kết quả cần đạt | Person in charge |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Week 1 | Database Setup & Clean ETL Pipeline | SQL Database schemas, pandas ETL script with outlier capping | Research Team |
| **2** | Week 2 | RFM Feature Engineering & Baseline Models | Customer RFM metric mapping, logistic regression model (98.6% Acc) | Research Team |
| **3** | Week 3 | T-Learner XGBoost Model Development | Trained Control/Treatment XGBoost models, custom CATE predictions | Research Team |
| **4** | Week 4 | Model Evaluation & Optimization | Qini Curve and AUUC evaluation metrics, feature importance plots | Research Team |
| **5** | Week 5 | API & Web Application Deployment | Flask REST API, Streamlit What-If simulation dashboard | Research Team |

---

## 7. Computational Resource Requirements / Yêu cầu tài nguyên tính toán
A standard local development computer (8GB RAM, CPU i5 or equivalent) running Python 3.8+ and SQL Server. No external GPU clusters or paid APIs are required.

---

## 8. Expected Results / Dự kiến kết quả đề tài
The proposal is expected to result in a functional prototype that optimizes marketing spend. Methodologically, we expect to demonstrate that targeting only high-uplift Persuadables yields a higher ROI compared to mass-mailing. The deliverables include: (i) the clean SQL database structure, (ii) saved Python model files (.pkl), (iii) an active Streamlit dashboard, and (iv) a 10-page scientific LaTeX research paper ready for submission.

---

## 9. References / Tài liệu tham khảo
1. Künzel, S. R., Sekhon, J. S., Bickel, P. J., & Yu, B. (2019). Metalearners for estimating heterogeneous treatment effects using machine learning. *Proceedings of the National Academy of Sciences*, 116(10), 4156-4165.
2. Hughes, A. M. (1994). *Strategic database marketing*. Probus Publishing Company.
3. Radcliffe, N. J., & Surry, P. D. (2011). Real-world uplift modelling with significance-based uplift trees. *White Paper, Stochastic Solutions*, 28, 1-18.
4. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. In *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785-794).
5. Chen, D. (2012). Online Retail II. *UCI Machine Learning Repository*. https://doi.org/10.24432/C5CG6D
