# Blinq

An AI-powered data analyst agent that helps you analyze and visualize your CSV data through natural language queries. Currently supports CSV files only.

## Project Status

**Backend**: Complete - AI agent, authentication, Razorpay payment integration, and query quota system all implemented. Also supports Grafana Prometheus for logging

**Frontend**: Integration with backend APIs in progress - UI components and pages (some pages remain) are built

# TODO
- [ ] Add password change feature using OTP
- [ ] Add Loki on Grafana (only `auth.py` is done for now, need to do for all)
- [ ] Frontend code up
- [ ] Add conversation history (state) to the agent
- [ ] Add deployment scripts and docker files
- [ ] Add deeper analysis- this would require the agent to write complete python code in secure executable sandbox unlike the simple polars SQL queries. This would help in analysis queries which require more deeper code execution like forecasting using ARIMA and all

Why this if ChatGPT and Claude can already do this?
The thing is they cannot if you are up for some serious data analysis. 

This-
<img width="1240" height="1068" alt="image" src="https://github.com/user-attachments/assets/ab74d82d-5bd2-4dce-a876-99c58245a181" />
