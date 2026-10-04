import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import (
    CriticalIssue,
    Issue,
    LowPriorityIssue,
    Reporter,
)


BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

REPORTERS_FILE = os.path.join(BASE_DIR, "reporters.json")
ISSUES_FILE = os.path.join(BASE_DIR, "issues.json")


def read_json_file(file_path):
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def write_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


@csrf_exempt
def reporters(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400,
            )

        required_fields = ["id", "name", "email", "team"]

        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"Missing field: {field}"},
                    status=400,
                )

        reporter = Reporter(
            data["id"],
            data["name"],
            data["email"],
            data["team"],
        )

        try:
            reporter.validate()
        except ValueError as error:
            return JsonResponse(
                {"error": str(error)},
                status=400,
            )

        reporters_data = read_json_file(REPORTERS_FILE)

        if any(item["id"] == reporter.id for item in reporters_data):
            return JsonResponse(
                {"error": "Reporter ID already exists"},
                status=400,
            )

        reporter_data = reporter.to_dict()
        reporters_data.append(reporter_data)
        write_json_file(REPORTERS_FILE, reporters_data)

        return JsonResponse(
            reporter_data,
            status=201,
        )

    if request.method == "GET":
        reporters_data = read_json_file(REPORTERS_FILE)
        reporter_id = request.GET.get("id")

        if reporter_id is not None:
            try:
                reporter_id = int(reporter_id)
            except ValueError:
                return JsonResponse(
                    {"error": "Invalid reporter id"},
                    status=400,
                )

            for reporter in reporters_data:
                if reporter["id"] == reporter_id:
                    return JsonResponse(reporter)

            return JsonResponse(
                {"error": "Reporter not found"},
                status=404,
            )

        return JsonResponse(
            reporters_data,
            safe=False,
        )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405,
    )


@csrf_exempt
def issues(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400,
            )

        required_fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "reporter_id",
        ]

        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"Missing field: {field}"},
                    status=400,
                )

        reporters_data = read_json_file(REPORTERS_FILE)

        reporter_exists = any(
            reporter["id"] == data["reporter_id"]
            for reporter in reporters_data
        )

        if not reporter_exists:
            return JsonResponse(
                {"error": "Reporter not found"},
                status=400,
            )

        priority = data["priority"]

        if priority == "critical":
            issue = CriticalIssue(
                data["id"],
                data["title"],
                data["description"],
                data["status"],
                data["priority"],
                data["reporter_id"],
            )
        elif priority == "low":
            issue = LowPriorityIssue(
                data["id"],
                data["title"],
                data["description"],
                data["status"],
                data["priority"],
                data["reporter_id"],
            )
        else:
            issue = Issue(
                data["id"],
                data["title"],
                data["description"],
                data["status"],
                data["priority"],
                data["reporter_id"],
            )

        try:
            issue.validate()
        except ValueError as error:
            return JsonResponse(
                {"error": str(error)},
                status=400,
            )

        issues_data = read_json_file(ISSUES_FILE)

        if any(item["id"] == issue.id for item in issues_data):
            return JsonResponse(
                {"error": "Issue ID already exists"},
                status=400,
            )

        issue_data = issue.to_dict()
        issue_data["message"] = issue.describe()

        issues_data.append(issue_data)
        write_json_file(ISSUES_FILE, issues_data)

        return JsonResponse(
            issue_data,
            status=201,
        )

    if request.method == "GET":
        issues_data = read_json_file(ISSUES_FILE)
        issue_id = request.GET.get("id")
        status_filter = request.GET.get("status")

        if issue_id is not None:
            try:
                issue_id = int(issue_id)
            except ValueError:
                return JsonResponse(
                    {"error": "Invalid issue id"},
                    status=400,
                )

            for issue in issues_data:
                if issue["id"] == issue_id:
                    return JsonResponse(issue)

            return JsonResponse(
                {"error": "Issue not found"},
                status=404,
            )

        if status_filter is not None:
            filtered_issues = [
                issue
                for issue in issues_data
                if issue["status"] == status_filter
            ]

            return JsonResponse(
                filtered_issues,
                safe=False,
            )

        return JsonResponse(
            issues_data,
            safe=False,
        )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405,
    )
