from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Iterable, Set, List, Dict, Union


class AttendanceTracker:
    """Manage attendance for a single class session.

    Responsibilities:
    - track a roster of student IDs
    - mark students present/absent
    - persist/load attendance to/from CSV or JSON

    Contract (inputs/outputs):
    - constructor accepts an iterable of student ID strings
    - mark/clear methods mutate internal state
    - save/load methods accept file paths (str or Path)

    Error modes:
    - ValueError when an operation references an ID not in the roster
    """

    def __init__(self, class_roster: Iterable[str]):
        """Initialize tracker with a roster.

        Args:
            class_roster: iterable of unique student ID strings
        """
        self.roster: Set[str] = set(class_roster)
        self.present_students: Set[str] = set()

    def mark_present(self, student_id: str) -> None:
        """Mark a student as present.

        Raises ValueError if the student is not in the roster.
        """
        if student_id not in self.roster:
            raise ValueError(f"Student '{student_id}' is not in the class roster.")
        self.present_students.add(student_id)

    def mark_absent(self, student_id: str) -> None:
        """Mark a student as absent (remove present flag).

        Raises ValueError if the student is not in the roster.
        """
        if student_id not in self.roster:
            raise ValueError(f"Student '{student_id}' is not in the class roster.")
        self.present_students.discard(student_id)

    def clear(self) -> None:
        """Clear all present marks for a fresh session."""
        self.present_students.clear()

    def get_absent_students(self) -> Set[str]:
        """Return set of students in roster but not marked present."""
        return self.roster - self.present_students

    def get_attendance_list(self) -> List[str]:
        """Return a sorted list of present student IDs."""
        return sorted(self.present_students)

    def percent_present(self) -> float:
        """Return fraction (0..100) of roster marked present.

        Returns 0.0 when roster is empty.
        """
        total = len(self.roster)
        if total == 0:
            return 0.0
        return (len(self.present_students) / total) * 100.0

    # --- persistence helpers ---
    def to_dict(self) -> Dict[str, List[str]]:
        """Serialize to a plain dict.

        Format: {"roster": [...], "present": [...]} with lists of IDs.
        """
        return {"roster": sorted(self.roster), "present": sorted(self.present_students)}

    @classmethod
    def from_dict(cls, data: Dict[str, Iterable[str]]) -> "AttendanceTracker":
        """Create an AttendanceTracker from a dict produced by `to_dict`."""
        roster = data.get("roster", [])
        present = set(data.get("present", []))
        at = cls(roster)
        # only keep present IDs that are in the roster
        at.present_students = {s for s in present if s in at.roster}
        return at

    def save_json(self, path: Union[str, Path]) -> None:
        """Save tracker state to a JSON file.

        The JSON contains the `roster` and the `present` lists.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_json(cls, path: Union[str, Path]) -> "AttendanceTracker":
        """Load tracker state from a JSON file."""
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_csv(self, path: Union[str, Path]) -> None:
        """Save attendance to CSV with columns: id,present

        present column will be '1' for present, '0' for absent.
        """
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "present"])
            for sid in sorted(self.roster):
                writer.writerow([sid, "1" if sid in self.present_students else "0"])

    @classmethod
    def load_csv(cls, path: Union[str, Path]) -> "AttendanceTracker":
        """Load attendance from a CSV created by `save_csv`.

        Accepts truthy values in the `present` column like 1/true/yes.
        """
        p = Path(path)
        roster: List[str] = []
        present: Set[str] = set()
        with p.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = row.get("id")
                if sid is None:
                    continue
                roster.append(sid)
                val = (row.get("present") or "").strip().lower()
                if val in {"1", "true", "t", "yes", "y"}:
                    present.add(sid)
        at = cls(roster)
        at.present_students = {s for s in present if s in at.roster}
        return at

    def __repr__(self) -> str:
        return f"AttendanceTracker(roster={len(self.roster)} students, present={len(self.present_students)})"

