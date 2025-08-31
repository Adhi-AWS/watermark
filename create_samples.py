import pandas as pd
import os

# Create sample Excel files for testing
def create_sample_files():
    """Create sample Excel files for testing the secure viewer"""
    
    # Sample data for different sheets
    employee_data = {
        'Employee ID': [1001, 1002, 1003, 1004, 1005],
        'Name': ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Wilson', 'Tom Brown'],
        'Department': ['IT', 'Finance', 'HR', 'Marketing', 'IT'],
        'Salary': [75000, 65000, 80000, 70000, 78000],
        'Start Date': ['2020-01-15', '2019-03-10', '2021-06-01', '2020-11-20', '2021-01-05']
    }
    
    financial_data = {
        'Quarter': ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
        'Revenue': [1200000, 1350000, 1280000, 1450000],
        'Expenses': [800000, 900000, 850000, 950000],
        'Profit': [400000, 450000, 430000, 500000],
        'Growth %': [8.5, 12.3, 6.7, 15.2]
    }
    
    project_data = {
        'Project Name': ['Project Alpha', 'Project Beta', 'Project Gamma', 'Project Delta'],
        'Status': ['Completed', 'In Progress', 'On Hold', 'Planning'],
        'Budget': [250000, 180000, 320000, 150000],
        'Start Date': ['2024-01-01', '2024-03-15', '2024-02-10', '2024-06-01'],
        'End Date': ['2024-06-30', '2024-09-30', '2024-12-31', '2024-11-15']
    }
    
    # Create directory if it doesn't exist
    os.makedirs('secure_files', exist_ok=True)
    
    # Create Employee Data file
    with pd.ExcelWriter('secure_files/employee_data.xlsx') as writer:
        pd.DataFrame(employee_data).to_excel(writer, sheet_name='Employees', index=False)
        pd.DataFrame({
            'Department': ['IT', 'Finance', 'HR', 'Marketing'],
            'Employee Count': [2, 1, 1, 1],
            'Avg Salary': [76500, 65000, 80000, 70000]
        }).to_excel(writer, sheet_name='Department Summary', index=False)
    
    # Create Financial Report file
    with pd.ExcelWriter('secure_files/financial_report.xlsx') as writer:
        pd.DataFrame(financial_data).to_excel(writer, sheet_name='Quarterly Results', index=False)
        pd.DataFrame({
            'Metric': ['Total Revenue', 'Total Expenses', 'Net Profit', 'Avg Growth'],
            'Value': [5280000, 3500000, 1780000, 10.7]
        }).to_excel(writer, sheet_name='Annual Summary', index=False)
    
    # Create Project Status file
    with pd.ExcelWriter('secure_files/project_status.xlsx') as writer:
        pd.DataFrame(project_data).to_excel(writer, sheet_name='Projects', index=False)
        pd.DataFrame({
            'Status': ['Completed', 'In Progress', 'On Hold', 'Planning'],
            'Count': [1, 1, 1, 1],
            'Total Budget': [250000, 180000, 320000, 150000]
        }).to_excel(writer, sheet_name='Status Summary', index=False)
    
    print("Sample Excel files created successfully:")
    print("- secure_files/employee_data.xlsx")
    print("- secure_files/financial_report.xlsx") 
    print("- secure_files/project_status.xlsx")

if __name__ == "__main__":
    create_sample_files()
