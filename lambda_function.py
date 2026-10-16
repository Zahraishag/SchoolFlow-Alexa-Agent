from schoolflow_agent import run_schoolflow


# =========================================================
# ALEXA RESPONSE
# =========================================================

def alexa_response(
    text,
    session_attributes=None,
    end_session=False
):
    """
    Build a valid Alexa response.
    """

    response = {
        "version": "1.0",
        "sessionAttributes": session_attributes or {},
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": text
            },
            "shouldEndSession": end_session
        }
    }

    # Keep Alexa listening when the workflow
    # still requires human approval.
    if not end_session:
        response["response"]["reprompt"] = {
            "outputSpeech": {
                "type": "PlainText",
                "text": (
                    "Please say approve or reject."
                )
            }
        }

    return response


# =========================================================
# SLOT HELPERS
# =========================================================

def get_slot(intent, slot_name):
    """
    Safely read a slot value from an Alexa intent.
    """

    slots = intent.get("slots", {})
    slot = slots.get(slot_name, {})

    return slot.get("value")


def normalize_period(period):
    """
    Convert Alexa period value to an integer
    when possible.
    """

    if period is None:
        return 2

    try:
        return int(period)

    except (TypeError, ValueError):
        period_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8
        }

        return period_words.get(
            str(period).lower(),
            2
        )


# =========================================================
# MAIN LAMBDA HANDLER
# =========================================================

def lambda_handler(event, context):

    request = event.get(
        "request",
        {}
    )

    request_type = request.get(
        "type"
    )

    session_attributes = (
        event
        .get("session", {})
        .get("attributes", {})
        or {}
    )

    # =====================================================
    # 1. LAUNCH SCHOOLFLOW
    # =====================================================

    if request_type == "LaunchRequest":

        return alexa_response(
            (
                "Welcome to SchoolFlow. "
                "Tell me which teacher is absent."
            ),
            session_attributes
        )

    # =====================================================
    # 2. INTENT REQUEST
    # =====================================================

    if request_type == "IntentRequest":

        intent = request.get(
            "intent",
            {}
        )

        intent_name = intent.get(
            "name"
        )

        # -------------------------------------------------
        # TEACHER ABSENCE
        # -------------------------------------------------

        if intent_name == "TeacherAbsenceIntent":

            teacher_name = (
                get_slot(
                    intent,
                    "teacherName"
                )
                or "Nora"
            )

            day = (
                get_slot(
                    intent,
                    "day"
                )
                or "Sunday"
            )

            period = normalize_period(
                get_slot(
                    intent,
                    "period"
                )
            )

            # Start a new absence workflow.
            rejected_candidates = []

            try:

                result = run_schoolflow(
                    action="recommend",
                    absent_teacher=teacher_name,
                    day=day,
                    period=period,
                    rejected_candidates=(
                        rejected_candidates
                    )
                )

            except Exception as error:

                print(
                    "SchoolFlow recommendation error:",
                    str(error)
                )

                return alexa_response(
                    (
                        "SchoolFlow could not complete "
                        "the recommendation. "
                        "Please try again."
                    ),
                    session_attributes,
                    True
                )

            # No safe candidate found.
            if result.get("status") == "escalate":

                return alexa_response(
                    result.get(
                        "message",
                        (
                            "No safe substitute is "
                            "available. The case has "
                            "been escalated to the "
                            "administrator."
                        )
                    ),
                    session_attributes,
                    True
                )

            candidate = result.get(
                "candidate"
            )

            score = result.get(
                "score"
            )

            reason = result.get(
                "reason",
                "validated by SchoolFlow"
            )

            # Save workflow state in Alexa session.
            session_attributes.update({
                "absentTeacher": teacher_name,
                "day": day,
                "period": period,
                "pendingCandidate": candidate,
                "rejectedCandidates": (
                    rejected_candidates
                )
            })

            return alexa_response(
                (
                    f"{candidate} is the recommended "
                    f"substitute for {teacher_name} "
                    f"on {day}, period {period}. "
                    f"SchoolFlow score is {score}. "
                    f"Reason: {reason}. "
                    f"Would you like to approve "
                    f"or reject {candidate}?"
                ),
                session_attributes
            )

        # -------------------------------------------------
        # APPROVE SUBSTITUTE
        # -------------------------------------------------

        if intent_name == "SubstituteDecisionIntent":

            candidate = (
                get_slot(
                    intent,
                    "teacherName"
                )
                or session_attributes.get(
                    "pendingCandidate"
                )
            )

            if not candidate:

                return alexa_response(
                    (
                        "There is no pending substitute "
                        "recommendation."
                    ),
                    session_attributes
                )

            absent_teacher = (
                session_attributes.get(
                    "absentTeacher",
                    "Nora"
                )
            )

            day = (
                session_attributes.get(
                    "day",
                    "Sunday"
                )
            )

            period = normalize_period(
                session_attributes.get(
                    "period",
                    2
                )
            )

            try:

                result = run_schoolflow(
                    action="approve",
                    absent_teacher=absent_teacher,
                    day=day,
                    period=period,
                    candidate=candidate,
                    rejected_candidates=(
                        session_attributes.get(
                            "rejectedCandidates",
                            []
                        )
                    )
                )

            except Exception as error:

                print(
                    "SchoolFlow approval error:",
                    str(error)
                )

                return alexa_response(
                    (
                        "SchoolFlow could not complete "
                        "the approval workflow. "
                        "Please try again."
                    ),
                    session_attributes,
                    True
                )

            if result.get("status") != "completed":

                return alexa_response(
                    result.get(
                        "message",
                        (
                            "The schedule could not "
                            "be updated."
                        )
                    ),
                    session_attributes,
                    True
                )

            return alexa_response(
                result.get(
                    "message",
                    (
                        f"{candidate} has been approved."
                    )
                ),
                session_attributes,
                True
            )

        # -------------------------------------------------
        # REJECT SUBSTITUTE
        # -------------------------------------------------

        if intent_name == "RejectSubstituteIntent":

            candidate = (
                get_slot(
                    intent,
                    "teacherName"
                )
                or session_attributes.get(
                    "pendingCandidate"
                )
            )

            if not candidate:

                return alexa_response(
                    (
                        "There is no pending substitute "
                        "recommendation."
                    ),
                    session_attributes
                )

            absent_teacher = (
                session_attributes.get(
                    "absentTeacher",
                    "Nora"
                )
            )

            day = (
                session_attributes.get(
                    "day",
                    "Sunday"
                )
            )

            period = normalize_period(
                session_attributes.get(
                    "period",
                    2
                )
            )

            rejected_candidates = (
                session_attributes.get(
                    "rejectedCandidates",
                    []
                )
            )

            try:

                result = run_schoolflow(
                    action="reject",
                    absent_teacher=absent_teacher,
                    day=day,
                    period=period,
                    candidate=candidate,
                    rejected_candidates=(
                        rejected_candidates
                    )
                )

            except Exception as error:

                print(
                    "SchoolFlow rejection error:",
                    str(error)
                )

                return alexa_response(
                    (
                        "SchoolFlow could not "
                        "re-evaluate the candidates. "
                        "Please try again."
                    ),
                    session_attributes,
                    True
                )

            # No candidate remains.
            if result.get("status") == "escalate":

                session_attributes[
                    "rejectedCandidates"
                ] = result.get(
                    "rejected_candidates",
                    rejected_candidates
                )

                return alexa_response(
                    result.get(
                        "message",
                        (
                            "No safe substitute remains. "
                            "The case has been escalated "
                            "to the administrator."
                        )
                    ),
                    session_attributes,
                    True
                )

            next_candidate = result.get(
                "next_candidate"
            )

            score = result.get(
                "score"
            )

            reason = result.get(
                "reason",
                "validated by SchoolFlow"
            )

            session_attributes[
                "rejectedCandidates"
            ] = result.get(
                "rejected_candidates",
                rejected_candidates
            )

            session_attributes[
                "pendingCandidate"
            ] = next_candidate

            return alexa_response(
                (
                    f"{candidate} was rejected. "
                    f"The next recommended substitute "
                    f"is {next_candidate}. "
                    f"SchoolFlow score is {score}. "
                    f"Reason: {reason}. "
                    f"Would you like to approve "
                    f"or reject {next_candidate}?"
                ),
                session_attributes
            )

        # -------------------------------------------------
        # AMAZON HELP INTENT
        # -------------------------------------------------

        if intent_name == "AMAZON.HelpIntent":

            return alexa_response(
                (
                    "You can tell me that a teacher "
                    "is absent, for example, "
                    "Nora is absent on Sunday "
                    "during period two."
                ),
                session_attributes
            )

        # -------------------------------------------------
        # AMAZON STOP / CANCEL
        # -------------------------------------------------

        if intent_name in [
            "AMAZON.StopIntent",
            "AMAZON.CancelIntent"
        ]:

            return alexa_response(
                "Goodbye from SchoolFlow.",
                session_attributes,
                True
            )

    # =====================================================
    # 3. FALLBACK
    # =====================================================

    return alexa_response(
        (
            "Sorry, I did not understand that request. "
            "Please report a teacher absence, "
            "or say approve or reject."
        ),
        session_attributes
    )
