import pandas as pd
input_file = r'C:\Users\Akshat Jagdev\Downloads\export_project_20260903_194407.xls'
output_file = r'C:\Users\Akshat Jagdev\Desktop\aquarium_v0\export_project_latest.csv'
try:
    df = pd.read_excel(input_file, engine='xlrd')
    df.to_csv(output_file, index=False)
    print(f"Successfully converted")
except Exception as e:
    print(f"Error: {e}")
