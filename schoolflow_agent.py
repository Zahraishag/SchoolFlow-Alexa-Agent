from strands import Agent, tool
from strands.models import BedrockModel


# =========================================================
# SCHOOL DATA
# =========================================================

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


# =========================================================
# CORE SCHOOLFLOW LOGIC
# =========================================================

def get_teacher(teacher_name):
    return next(
        (
            teacher
            for teacher in teachers
            if teacher["name"].lower() == teacher_name.lower()
        ),
        None
    )


def get_affected_lesson(
    absent_teacher,
    day,
    period
):
    return next(
        (
            lesson
            for lesson in schedule
            if lesson["teacher"].lower() == absent_teacher.lower()
            and lesson["day"].lower() == day.lower()
            and lesson["period"] == int(period)
        ),
        None
    )


def find_candidates(absent_teacher):
    return [
        teacher
        for teacher in teachers
        if teacher["name"].lower() != absent_teacher.lower()
    ]


def has_conflict(
    teacher_name,
    day,
    period
):
    return any(
        lesson["teacher"].lower() == teacher_name.lower()
        and lesson["day"].lower() == day.lower()
        and lesson["period"] == int(period)
        for lesson in schedule
    )


def rank_candidates(
    absent_teacher,
    day,
    period,
    rejected_candidates=None
):
    rejected_candidates = rejected_candidates or []

    rejected_names = {
        name.lower()
        for name in rejected_candidates
    }

    absent_data = get_teacher(
        absent_teacher
    )

    if not absent_data:
        return []

    ranked = []

    for candidate in find_candidates(
        absent_teacher
    ):

        if candidate["name"].lower() in rejected_names:
            continue

        if has_conflict(
            candidate["name"],
            day,
            period
        ):
            continue

        # Hard safety rule
        if candidate["workload"] >= 6:
            continue

        score = 0
        reasons = []

        if (
            candidate["subject"]
            == absent_data["subject"]
        ):
            score += 3
            reasons.append("same subject")

        if (
            candidate["stage"]
            == absent_data["stage"]
        ):
            score += 2
            reasons.append("same stage")

        if candidate["workload"] < 6:
            score += 2
            reasons.append("acceptable workload")

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


# =========================================================
# STRANDS TOOLS
# =========================================================

@tool
def recommend_substitute(
    absent_teacher: str,
    day: str,
    period: int
) -> dict:
    """
    Recommend the safest substitute teacher.
    """

    ranked = rank_candidates(
        absent_teacher=absent_teacher,
        day=day,
        period=period
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
def check_teacher_conflict(
    teacher_name: str,
    day: str,
    period: int
) -> dict:
    """
    Check whether a teacher already has
    another lesson at the requested time.
    """

    conflict = has_conflict(
        teacher_name,
        day,
        period
    )

    return {
        "teacher": teacher_name,
        "conflict": conflict
    }


@tool
def check_teacher_workload(
    teacher_name: str
) -> dict:
    """
    Check teacher workload.
    """

    teacher = get_teacher(
        teacher_name
    )

    if not teacher:
        return {
            "status": "error",
            "message": "Teacher not found."
        }

    return {
        "teacher": teacher_name,
        "workload": teacher["workload"],
        "eligible": teacher["workload"] < 6
    }


@tool
def human_approval(
    teacher_name: str,
    decision: str
) -> dict:
    """
    Record explicit human approval or rejection.
    """

    decision = decision.lower()

    if decision == "approve":
        return {
            "status": "approved",
            "teacher": teacher_name
        }

    if decision == "reject":
        return {
            "status": "rejected",
            "teacher": teacher_name
        }

    return {
        "status": "invalid",
        "message": (
            "Decision must be approve or reject."
        )
    }


@tool
def update_schedule(
    teacher_name: str,
    absent_teacher: str,
    day: str,
    period: int
) -> dict:
    """
    Update the school schedule after approval.
    """

    affected_lesson = get_affected_lesson(
        absent_teacher,
        day,
        period
    )

    if not affected_lesson:
        return {
            "status": "error",
            "message": "Affected lesson not found."
        }

    lesson = {
        "teacher": teacher_name,
        "day": day,
        "period": int(period),
        "class": affected_lesson["class"],
        "subject": affected_lesson["subject"]
    }

    schedule.append(
        lesson
    )

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
    """
    Prepare notification for the approved substitute.
    """

    message = (
        f"{teacher_name}, you have been assigned "
        f"to {class_name} {subject} "
        f"on {day}, period {period}."
    )

    return {
        "status": "notification_ready",
        "teacher": teacher_name,
        "message": message
    }


# =========================================================
# STRANDS AGENT
# =========================================================

_agent = None


def create_agent():
    """
    Create the SchoolFlow Strands Agent.

    AWS credentials are expected to come from
    the AWS execution environment / IAM role.
    No secret keys are stored in source code.
    """

    model = BedrockModel(
        region_name="us-east-1",
        model_id="us.anthropic.claude-sonnet-4-6"
    )

    return Agent(
        model=model,
        tools=[
            recommend_substitute,
            check_teacher_conflict,
            check_teacher_workload,
            human_approval,
            update_schedule,
            notify_substitute
        ],
        system_prompt="""
You are SchoolFlow, an AI school operations agent.

Your purpose is to safely help schools manage
teacher absences and substitute assignments.

SAFETY RULES:

1. Never invent teachers or schedule data.

2. A substitute must not have a schedule conflict.

3. A teacher with workload 6 or greater
   must not be recommended.

4. Prefer:
   - same subject
   - same school stage
   - lower workload

5. Never assign a substitute automatically.

6. A human administrator must explicitly
   approve or reject the recommendation.

7. Schedule updates are allowed only after
   explicit human approval.

8. Notifications happen only after
   a successful schedule update.

9. If a candidate is rejected,
   recommend another eligible candidate.

10. If no safe candidate exists,
    escalate to the administrator.

Core principle:

AI recommends.
Human approves.
System executes safely.
"""
    )


def get_agent():
    global _agent

    if _agent is None:
        _agent = create_agent()

    return _agent


# =========================================================
# LAMBDA ENTRY POINT
# =========================================================

def run_schoolflow(
    action,
    absent_teacher="Nora",
    day="Sunday",
    period=2,
    candidate=None,
    rejected_candidates=None
):
    """
    Single entry point used by AWS Lambda.

    Supported actions:
    - recommend
    - approve
    - reject
    """

    rejected_candidates = (
        rejected_candidates or []
    )

    # -----------------------------------------
    # RECOMMEND
    # -----------------------------------------

    if action == "recommend":

        ranked = rank_candidates(
            absent_teacher=absent_teacher,
            day=day,
            period=int(period),
            rejected_candidates=rejected_candidates
        )

        if not ranked:
            return {
                "status": "escalate",
                "message": (
                    "No safe substitute remains. "
                    "Escalate to the administrator."
                )
            }

        recommendation = ranked[0]

        # Invoke the Strands agent so the
        # recommendation is part of the
        # actual agentic execution path.
        agent = get_agent()

        agent_prompt = (
            f"Teacher {absent_teacher} is absent "
            f"on {day}, period {period}. "
            f"The validated safest candidate is "
            f"{recommendation['name']} with score "
            f"{recommendation['score']}. "
            f"Reason: {recommendation['reason']}. "
            f"Present this recommendation clearly "
            f"and request explicit human approval. "
            f"Do not update the schedule."
        )

        agent_result = agent(
            agent_prompt
        )

        return {
            "status": "recommendation",
            "candidate": recommendation["name"],
            "score": recommendation["score"],
            "reason": recommendation["reason"],
            "agent_response": str(agent_result)
        }

    # -----------------------------------------
    # REJECT
    # -----------------------------------------

    if action == "reject":

        if not candidate:
            return {
                "status": "error",
                "message": (
                    "Candidate name is required."
                )
            }

        if candidate not in rejected_candidates:
            rejected_candidates.append(
                candidate
            )

        ranked = rank_candidates(
            absent_teacher=absent_teacher,
            day=day,
            period=int(period),
            rejected_candidates=rejected_candidates
        )

        if not ranked:
            return {
                "status": "escalate",
                "rejected_candidates": rejected_candidates,
                "message": (
                    "Candidate rejected. "
                    "No safe substitute remains."
                )
            }

        next_candidate = ranked[0]

        return {
            "status": "rejected",
            "rejected": candidate,
            "rejected_candidates": rejected_candidates,
            "next_candidate": next_candidate["name"],
            "score": next_candidate["score"],
            "reason": next_candidate["reason"]
        }

    # -----------------------------------------
    # APPROVE
    # -----------------------------------------

    if action == "approve":

        if not candidate:
            return {
                "status": "error",
                "message": (
                    "Candidate name is required."
                )
            }

        approval = {
            "status": "approved",
            "teacher": candidate
        }

        update_result = update_schedule(
            teacher_name=candidate,
            absent_teacher=absent_teacher,
            day=day,
            period=int(period)
        )

        if update_result.get("status") != "updated":
            return update_result

        lesson = update_result["lesson"]

        notification = notify_substitute(
            teacher_name=candidate,
            day=day,
            period=int(period),
            class_name=lesson["class"],
            subject=lesson["subject"]
        )

        return {
            "status": "completed",
            "approval": approval,
            "schedule": update_result,
            "notification": notification,
            "message": (
                f"{candidate} is approved. "
                f"The schedule has been updated for "
                f"{lesson['class']} {lesson['subject']} "
                f"on {day}, period {period}. "
                f"{candidate} has been notified."
            )
        }

    return {
        "status": "error",
        "message": (
            "Unknown action. "
            "Use recommend, approve, or reject."
        )
    }
