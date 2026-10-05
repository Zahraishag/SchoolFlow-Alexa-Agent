from strands import Agent, tool
from strands.models import BedrockModel


teachers = [
    {
        "name": "Nora",
        "subject": "Math",
        "stage": "Intermediate",
        "workload": 5
    },
    {
        "name": "Sara",
        "subject": "Math",
        "stage": "Intermediate",
        "workload": 4
    },
    {
        "name": "Reem",
        "subject": "Math",
        "stage": "Intermediate",
        "workload": 6
    },
    {
        "name": "Amal",
        "subject": "Science",
        "stage": "Intermediate",
        "workload": 3
    },
    {
        "name": "Huda",
        "subject": "Math",
        "stage": "Primary",
        "workload": 4
    }
]


schedule = [
    {
        "teacher": "Nora",
        "day": "Sunday",
        "period": 2,
        "class": "Grade 5",
        "subject": "Math"
    },
    {
        "teacher": "Nora",
        "day": "Sunday",
        "period": 4,
        "class": "Grade 6",
        "subject": "Math"
    },
    {
        "teacher": "Sara",
        "day": "Sunday",
        "period": 1,
        "class": "Grade 6",
        "subject": "Math"
    },
    {
        "teacher": "Reem",
        "day": "Sunday",
        "period": 2,
        "class": "Grade 7",
        "subject": "Math"
    },
    {
        "teacher": "Amal",
        "day": "Sunday",
        "period": 3,
        "class": "Grade 5",
        "subject": "Science"
    }
]


rejected_candidates = set()


def find_substitute_candidates(absent_teacher):
    return [
        teacher for teacher in teachers
        if teacher["name"] != absent_teacher
    ]


def rank_candidates(
    candidates,
    absent_teacher,
    day,
    period
):
    absent_data = next(
        teacher for teacher in teachers
        if teacher["name"] == absent_teacher
    )

    ranked = []

    for candidate in candidates:

        if candidate["name"] in rejected_candidates:
            continue

        conflict = any(
            lesson["teacher"] == candidate["name"]
            and lesson["day"] == day
            and lesson["period"] == period
            for lesson in schedule
        )

        if conflict:
            continue

        if candidate["workload"] >= 6:
            continue

        score = 0
        reasons = []

        if candidate["subject"] == absent_data["subject"]:
            score += 3
            reasons.append("same subject")

        if candidate["stage"] == absent_data["stage"]:
            score += 2
            reasons.append("same stage")

        if candidate["workload"] < 6:
            score += 2
            reasons.append("lower workload")

        ranked.append({
            "name": candidate["name"],
            "score": score,
            "reason": ", ".join(reasons)
        })

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return ranked


@tool
def recommend_substitute(
    absent_teacher: str,
    day: str,
    period: int
) -> dict:

    candidates = find_substitute_candidates(
        absent_teacher
    )

    ranked = rank_candidates(
        candidates,
        absent_teacher,
        day,
        period
    )

    if not ranked:
        return {
            "status": "escalate",
            "message": "No safe substitute found."
        }

    return {
        "status": "recommendation",
        "candidate": ranked[0]
    }


@tool
def human_approval(
    teacher_name: str,
    decision: str
) -> dict:

    decision = decision.lower()

    if decision == "approve":
        return {
            "status": "approved",
            "teacher": teacher_name
        }

    if decision == "reject":
        rejected_candidates.add(
            teacher_name
        )

        return {
            "status": "rejected",
            "teacher": teacher_name
        }

    return {
        "status": "invalid"
    }


@tool
def update_schedule(
    teacher_name: str,
    absent_teacher: str,
    day: str,
    period: int
) -> dict:

    affected_lesson = next(
        (
            lesson for lesson in schedule
            if lesson["teacher"] == absent_teacher
            and lesson["day"] == day
            and lesson["period"] == period
        ),
        None
    )

    if not affected_lesson:
        return {
            "status": "error",
            "message": "Affected lesson not found."
        }

    lesson = {
        "teacher": teacher_name,
        "day": day,
        "period": period,
        "class": affected_lesson["class"],
        "subject": affected_lesson["subject"]
    }

    schedule.append(lesson)

    return {
        "status": "updated",
        "lesson": lesson
    }


@tool
def notify_substitute(
    teacher_name: str,
    day: str,
    period: int,
    class_name: str,
    subject: str
) -> dict:

    return {
        "status": "notification_ready",
        "message": (
            f"{teacher_name} assigned to "
            f"{class_name} {subject}, "
            f"{day}, period {period}."
        )
    }


def create_agent(api_key: str):

    model = BedrockModel(
        region_name="us-east-1",
        api_key=api_key,
        model_id="us.anthropic.claude-sonnet-4-6"
    )

    return Agent(
        model=model,
        tools=[
            recommend_substitute,
            human_approval,
            update_schedule,
            notify_substitute
        ],
        system_prompt="""
You are SchoolFlow, an AI school operations agent.

Rules:
1. Recommend the safest substitute.
2. Never assign automatically.
3. Wait for explicit human approval.
4. If rejected, remember the rejection and recommend again.
5. Only update the schedule after approval.
6. Notify the substitute after the schedule update.
7. If no safe substitute remains, escalate to the administrator.
8. Never invent schedule data.
"""
    )
