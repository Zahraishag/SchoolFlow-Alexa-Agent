## End-to-End Alexa Demo

SchoolFlow was successfully tested as an end-to-end voice-driven prototype through the Alexa Simulator.

### 1. Initial recommendation

Nora is reported absent on Sunday during period 2.

SchoolFlow evaluates eligible candidates using deterministic safety rules, including schedule conflicts, subject match, school stage, and workload.

Sara is ranked as the safest candidate and presented to the administrator for human approval.

![Sara recommendation](images/01-alexa-sara-recommendation.png)

### 2. Human rejection and re-ranking

The administrator rejects Sara.

SchoolFlow preserves the rejection in the active workflow, excludes Sara from reconsideration, re-ranks the remaining eligible candidates, and recommends Huda.

The system again waits for an explicit human decision.

### 3. Human approval and safe execution

The administrator approves Huda.

Only after approval does SchoolFlow update the prototype schedule state and prepare the substitute notification.

![Reject Sara and approve Huda](images/02-alexa-reject-huda-approval.png)

### Verified End-to-End Workflow

**Alexa → AWS Lambda → SchoolFlow Agent → Candidate Validation → Recommendation → Human Decision → Schedule Update → Notification Preparation**

### Safety Principle

**AI recommends → Deterministic rules validate → Human approves → System executes safely.**

## Development Friction Log

We documented the main implementation challenges, fixes, and improvement suggestions encountered while building SchoolFlow.

[Read the SchoolFlow Friction Log](friction_log.md)
