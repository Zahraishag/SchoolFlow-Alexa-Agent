def alexa_response(text, session_attributes=None, end_session=False):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes or {},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Please say approve or reject."
                }
            },
            "shouldEndSession": end_session
        }
    }


teachers = [
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


def get_slot(intent, slot_name):
    slots = intent.get("slots", {})
    slot = slots.get(slot_name, {})
    return slot.get("value")


def choose_substitute(rejected=None):
    rejected = rejected or []

    candidates = []

    for teacher in teachers:
        if teacher["name"] in rejected:
            continue

        if teacher["workload"] >= 6:
            continue

        score = 0
        reasons = []

        if teacher["subject"] == "Math":
            score += 3
            reasons.append("same subject")

        if teacher["stage"] == "Intermediate":
            score += 2
            reasons.append("same stage")

        if teacher["workload"] < 6:
            score += 2
            reasons.append("lower workload")

        candidates.append({
            "name": teacher["name"],
            "score": score,
            "reason": ", ".join(reasons)
        })

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates[0]


def lambda_handler(event, context):

    request = event.get("request", {})
    request_type = request.get("type")

    session_attributes = (
        event.get("session", {})
        .get("attributes", {})
    )

    # 1. Open SchoolFlow
    if request_type == "LaunchRequest":
        return alexa_response(
            "Welcome to SchoolFlow. "
            "Tell me which teacher is absent.",
            session_attributes
        )

    # 2. Intent handling
    if request_type == "IntentRequest":

        intent = request.get("intent", {})
        intent_name = intent.get("name")

        # ---------------------------------
        # Teacher absence
        # ---------------------------------
        if intent_name == "TeacherAbsenceIntent":

            teacher_name = (
                get_slot(intent, "teacherName")
                or "Nora"
            )

            day = (
                get_slot(intent, "day")
                or "Sunday"
            )

            period = (
                get_slot(intent, "period")
                or "2"
            )

            # Start a fresh recommendation chain
            session_attributes["rejectedCandidates"] = []

            candidate = choose_substitute([])

            if candidate is None:
                return alexa_response(
                    "No safe substitute is available. "
                    "The case should be escalated to the administrator.",
                    session_attributes,
                    True
                )

            session_attributes.update({
                "absentTeacher": teacher_name,
                "day": day,
                "period": period,
                "pendingCandidate": candidate["name"]
            })

            return alexa_response(
                f"{candidate['name']} is the recommended substitute "
                f"for {teacher_name} on {day}, period {period}. "
                f"Reason: {candidate['reason']}. "
                f"Would you like to approve or reject {candidate['name']}?",
                session_attributes
            )

        # ---------------------------------
        # Approve substitute
        # ---------------------------------
        if intent_name == "SubstituteDecisionIntent":

            candidate = session_attributes.get(
                "pendingCandidate"
            )

            if not candidate:
                return alexa_response(
                    "There is no pending substitute recommendation.",
                    session_attributes
                )

            absent_teacher = session_attributes.get(
                "absentTeacher",
                "Nora"
            )

            day = session_attributes.get(
                "day",
                "Sunday"
            )

            period = session_attributes.get(
                "period",
                "2"
            )

            return alexa_response(
                f"{candidate} is approved. "
                f"The schedule has been updated for Grade 5 Math "
                f"on {day}, period {period}. "
                f"{candidate} has been notified.",
                session_attributes,
                True
            )

        # ---------------------------------
        # Reject substitute
        # ---------------------------------
        if intent_name == "RejectSubstituteIntent":

            candidate = session_attributes.get(
                "pendingCandidate"
            )

            if not candidate:
                return alexa_response(
                    "There is no pending substitute recommendation.",
                    session_attributes
                )

            rejected = session_attributes.get(
                "rejectedCandidates",
                []
            )

            if candidate not in rejected:
                rejected.append(candidate)

            session_attributes[
                "rejectedCandidates"
            ] = rejected

            new_candidate = choose_substitute(
                rejected
            )

            if new_candidate is None:
                return alexa_response(
                    "No safe substitute remains. "
                    "The case has been escalated to the administrator.",
                    session_attributes,
                    True
                )

            session_attributes[
                "pendingCandidate"
            ] = new_candidate["name"]

            return alexa_response(
                f"{candidate} was rejected. "
                f"The next recommended substitute is "
                f"{new_candidate['name']}. "
                f"Reason: {new_candidate['reason']}. "
                f"Would you like to approve or reject "
                f"{new_candidate['name']}?",
                session_attributes
            )

    # 3. Fallback
    return alexa_response(
        "Sorry, I did not understand that request.",
        session_attributes
    )
