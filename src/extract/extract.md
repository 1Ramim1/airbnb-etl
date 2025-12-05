## EXTRACT: PROJECT REQUIREMENTS

As THE CUSTOMER,
I want a robust ETL pipeline that cleans, standardises, imputes, and enriches Airbnb listings data from a CSV source, ensuring all fields are high-quality and engineered features are added,so that Data Analysts and Data Scientists can perform accurate pricing, occupancy, and market competitiveness analysis.

## EPIC 1

```text
As a Data Analyst/Scientist,
I want the Airbnb listings data to be accessible in a structured format,
So that it can be transformed and analysed.
```

## EPIC 1 BREAKDOWN

### USER STORY 1 — Extract Airbnb Listings Data

```text
As a Data Analyst/Scientist,
I want to extract the Airbnb listings dataset from a CSV file, so that it is available in a DataFrame for cleaning and transformation.
```

### ACCEPTANCE CRITERIA:

- CSV is loaded successfully using Pandas

- Extraction completes in under 2 seconds

- Missing file or format errors are handled gracefully

- Data is returned as a Pandas DataFrame

- A log entry is created for successful extraction

- Unit tests verify the extraction process
