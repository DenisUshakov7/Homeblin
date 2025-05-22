from flask import Flask, request, jsonify, render_template
import pandas as pd
from dataclasses import dataclass
from typing import Dict

app = Flask(__name__, template_folder="templates")


@dataclass
class Student:
    student_id: int
    name: str
    group: int
    hw_01: int = 0
    hw_02: int = 0
    exam: int = 0


def load_data(hw01_path: str, hw02_path: str) -> Dict[int, Student]:
    df1 = pd.read_csv(hw01_path)
    df2 = pd.read_csv(hw02_path)

    students = {}

    for _, row in df1.iterrows():
        sid = int(row["student_id"])
        students[sid] = Student(
            student_id=sid,
            name=row["name"],
            group=int(row["group"]),
            hw_01=int(row["hw-01"] or 0)
        )

    for _, row in df2.iterrows():
        sid = int(row["student_id"])
        if sid in students:
            students[sid].hw_02 = int(row["hw-02"] or 0)
        else:
            students[sid] = Student(
                student_id=sid,
                name=row["name"],
                group=int(row["group"]),
                hw_02=int(row["hw-02"] or 0)
            )

    return students


students = load_data("hw-01.csv", "hw-02.csv")


@app.route("/names")
def names() -> Response:
    return jsonify({"names": [s.name for s in students.values()]})


@app.route("/<hw_name>/mean_score")
def mean_hw(hw_name: str) -> tuple[dict[str, Union[str, float]], int] | dict[str, float]:
    if hw_name not in ["hw-01", "hw-02"]:
        return {"error": "Invalid homework name"}, 400
    scores = [getattr(s, hw_name.replace("-", "_")) for s in students.values()]
    return {"mean_score": sum(scores) / len(scores)}


@app.route("/<hw_name>/<int:group_id>/mean_score")
def mean_hw_group(hw_name: str, group_id: int) -> tuple[dict[str, str], int] | dict[str, float]:
    if hw_name not in ["hw-01", "hw-02"]:
        return {"error": "Invalid homework name"}, 400
    scores = [getattr(s, hw_name.replace("-", "_")) for s in students.values() if s.group == group_id]
    if not scores:
        return {"error": "No students in group"}, 400
    return {"mean_score": sum(scores) / len(scores)}


@app.route("/mean_score")
def query_mean_score() -> tuple[dict[str, str], int] | dict[str, float]:
    group_id = request.args.get("group_id", type=int)
    hw_name = request.args.get("hw_name")
    if not group_id or not hw_name:
        return {"error": "Missing parameters"}, 400
    return mean_hw_group(hw_name, group_id)


@app.route("/mark")
def mark() -> tuple[dict[str, str], int] | dict[str, float]:
    sid = request.args.get("student_id", type=int)
    group_id = request.args.get("group_id", type=int)

    if sid:
        student = students.get(sid)
        if not student:
            return {"error": "Student not found"}, 400
        return {"mark": compute_mark(student.exam)}

    elif group_id:
        group = [s for s in students.values() if s.group == group_id]
        if not group:
            return {"error": "Group not found"}, 400
        marks = [compute_mark(s.exam) for s in group]
        return {"average_mark": sum(marks) / len(marks)}

    return {"error": "No parameters provided"}, 400


@app.route("/course_table")
def course_table() -> str | tuple[dict[str, str], int]:
    hw_name = request.args.get("hw_name")
    group_id = request.args.get("group_id", type=int)
    if not hw_name:
        return {"error": "hw_name required"}, 400

    filtered = [s for s in students.values() if not group_id or s.group == group_id]
    scores = [
        {"name": s.name, "group": s.group, "score": getattr(s, hw_name.replace("-", "_"))}
        for s in filtered
    ]
    return render_template("course_table.html", scores=scores, hw_name=hw_name)



def compute_mark(exam_score: int) -> int:
    if exam_score == 0:
        return 2
    elif 1 <= exam_score <= 50:
        return 4
    elif exam_score > 50:
        return 5
    return 2


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1337, debug=True)
