# 1. Dictionary storing student details (ID as key, details as nested dictionary)
students = {
    "STU001": {"name": "Alice", "Python": 85, "Mathematics": 92, "AI": 88},
    "STU002": {"name": "Bob", "Python": 38, "Mathematics": 65, "AI": 72},  # Failed in Python
    "STU003": {"name": "Charlie", "Python": 95, "Mathematics": 98, "AI": 96},  # Class Topper
    "STU004": {"name": "David", "Python": 55, "Mathematics": 45, "AI": 58},
    "STU005": {"name": "Emma", "Python": 72, "Mathematics": 35, "AI": 80}   # Failed in Math
}

# Function to assign letter grade based on percentage
def get_grade(percentage):
    if percentage >= 90: return 'A'
    elif percentage >= 80: return 'B'
    elif percentage >= 70: return 'C'
    elif percentage >= 50: return 'D'
    else: return 'F'

# 2. Process student records (Calculate Total, Percentage, and Grade)
MAX_MARKS_PER_SUBJECT = 100
PASS_MARK = 40

for s_id, data in students.items():
    total = data["Python"] + data["Mathematics"] + data["AI"]
    percentage = (total / (3 * MAX_MARKS_PER_SUBJECT)) * 100
    
    data["total"] = total
    data["percentage"] = round(percentage, 2)
    data["grade"] = get_grade(percentage)

# 3. Find the Class Topper
topper_id = max(students, key=lambda k: students[k]["percentage"])
topper = students[topper_id]

# 4. Identify students who failed in any subject
failed_students = []
for s_id, data in students.items():
    if data["Python"] < PASS_MARK or data["Mathematics"] < PASS_MARK or data["AI"] < PASS_MARK:
        failed_students.append(data["name"])

# 5. Sort students based on percentage (Descending order)
sorted_students = sorted(students.values(), key=lambda x: x["percentage"], reverse=True)

# --- DISPLAYING THE RESULTS ---
print("=" * 60)
print(f"{'NAME':<10}{'PYTHON':<8}{'MATH':<8}{'AI':<8}{'TOTAL':<8}{'PERCENT%':<10}{'GRADE':<5}")
print("-" * 60)
for s in sorted_students:
    print(f"{s['name']:<10}{s['Python']:<8}{s['Mathematics']:<8}{s['AI']:<8}{s['total']:<8}{s['percentage']:<10}{s['grade']:<5}")
print("=" * 60)

print(f"\n Class Topper: {topper['name']} with {topper['percentage']}%")

print(f"\n Students who failed in one or more subjects: {', '.join(failed_students) if failed_students else 'None'}")
