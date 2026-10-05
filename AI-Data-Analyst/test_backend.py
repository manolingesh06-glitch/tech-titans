import pandas as pd
from backend import ask_ai

df = pd.DataFrame({
    "name": ["Asha", "Ravi", "Meena", "Kumar", "Priya"],
    "department": ["IT", "IT", "HR", "HR", "Sales"],
    "salary": [50000, 60000, 40000, 45000, 55000],
})

code, result = ask_ai("Which department has the highest average salary?", df)
print("CODE THE AI WROTE:")
print(code)
print()
print("RESULT:")
print(result)