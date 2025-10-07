import requests
import pandas as pd
import os

BACKEND_API_URL = os.getenv("BACKEND_URL", "http://aro-backend-app:8080/api/metrics")

ANOMALY_REPORT_URL = "http://aro-backend-app:8080/api/anomalies/report"

def fetch_metrics():
    """
    Connects to the backend API and fetches all available metrics.
    
    Returns :
       list : A list of metric dictionaries, or an emtpy list if any error occurs.
    """
    print(f"Fetching metrics from {BACKEND_API_URL}...")
    try:
        response = requests.get(f"{BACKEND_API_URL}?size=2000", timeout=10)
        response.raise_for_status()
        data = response.json()
        metric_list = data.get('content', [])
        print(f"Successfully fetched {len(metric_list)} metric records.")
        return metric_list
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to the backend API. Details: {e}")
        return []
    
def detect_anomalies_modified_zscore(metrics):
    """
    Analyzes metrics using the robust Modified Z-score method.
    This method is preferred over the standard Z-score as it uses
    the median, which is not skewed by the presence of extreme outliers.
    
    Args:
       metrics (list): A list of metric dictionaries from the backend.
       
    Returns:
       pandas.DataFrame: A DataFrame containing only the anomalous rows.
    """
    if not metrics:
        print("No metrics to analyze.")
        return pd.DataFrame()
    
    df = pd.DataFrame(metrics)
    print("\n--- Data Analysis ---")
    print("Initial data received.")
    print(df)
    
    anomalies_found = []
    
    for metric_type, group in df.groupby('metricType'):
        group = group.copy()
        group['value'] = pd.to_numeric(group['value'], errors='coerce')
        group = group.dropna(subset=['value'])
        median_val = group['value'].median()
        deviation_from_median = abs(group['value'] - median_val)
        mad = deviation_from_median.median()
        
        print(f"\nAnalyzing '{metric_type}':")
        print(f"  - Median: {median_val:.4f}")
        print(f"  - Median Absolute Devaition (MAD): {mad:.4f}")
        
        
        if mad == 0:
            continue
        
        group['mod_z_score'] = 0.6745 * (group['value'] - median_val) / mad
        threshold = 3.5
        detected = group[abs(group['mod_z_score']) > threshold]
        
        if not detected.empty:
            print(f"  - SUCCESS: Found {len(detected)} anomalies for '{metric_type}'!")
            anomalies_found.append(detected)
            
    if anomalies_found:
        return pd.concat(anomalies_found, ignore_index=True)
    else:
        return pd.DataFrame()
    

if __name__ == "__main__":
    print("--- ML Worker Started ---")
    
    all_metrics = fetch_metrics()
    found_anomalies = detect_anomalies_modified_zscore(all_metrics)
    
    print("\n--- Anomaly Detection Report ---")
    if isinstance(found_anomalies, pd.DataFrame) and not found_anomalies.empty:
        report_columns = ['id', 'source', 'metricType', 'value', 'mod_z_score']
        print(found_anomalies[report_columns].to_string(index=False))
        
        print(f"\n--- Reporting {len(found_anomalies)} anomalies to the backend ---")
        for index, row in found_anomalies.iterrows():
            try:
                requests.post(ANOMALY_REPORT_URL, timeout=5)
                print(f"  - Sucessfully reported anomaly with ID: {row['id']}")
            except requests.exceptions.RequestException as e:
                print(f"  - Failed to report anomaly with ID: {row['id']}. Error: {e}")
                
    else:
        print("No anomalies detected.")

    print("\n--- Ml Worker Finished ---")