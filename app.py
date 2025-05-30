from flask import Flask, request, jsonify, render_templetes
from flask_cors import CORS

app = Flask(__name__, template_folder="templetes", static_folder="static")
CORS(app)  # Enable CORS for all routes

# In-memory storage
students = []

# Root route — serves your HTML UI
@app.route("/", methods=["GET"])
def home():
    return render_templetes("index.html")

# API: Get all students
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students), 200

# API: Add a new student
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()
    # Prevent duplicate roll numbers
    for s in students:
        if s["roll"] == data["roll"]:
            return jsonify({"error": "Roll number already exists"}), 400

    students.append({
        "name": data["name"],
        "roll": data["roll"],
        "department": data["department"]
    })
    return jsonify({"message": "Student added successfully"}), 201

# API: Update existing student (allows changing roll too)
@app.route("/students/<old_roll>", methods=["PUT"])
def update_student(old_roll):
    data = request.get_json()
    new_roll = data.get("roll", old_roll)
    new_name = data.get("name")
    new_department = data.get("department")

    # If roll changed, check for duplicates
    if new_roll != old_roll:
        for s in students:
            if s["roll"] == new_roll:
                return jsonify({"error": "New roll number already exists"}), 400

    # Find and update
    for student in students:
        if student["roll"] == old_roll:
            student["roll"] = new_roll
            student["name"] = new_name or student["name"]
            student["department"] = new_department or student["department"]
            return jsonify({"message": "Student updated successfully"}), 200

    return jsonify({"error": "Student not found"}), 404

# API: Delete a student
@app.route("/students/<roll>", methods=["DELETE"])
def delete_student(roll):
    global students
    original_count = len(students)
    students = [s for s in students if s["roll"] != roll]

    if len(students) == original_count:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"}), 200

# Run the app
if __name__ == "__main__":
    # When deployed, Render will use gunicorn; this is just for local testing
    app.run(debug=True, host="0.0.0.0")
