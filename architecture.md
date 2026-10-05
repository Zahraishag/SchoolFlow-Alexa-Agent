# SchoolFlow Architecture

SchoolFlow is designed as a voice-first agentic workflow for safe teacher substitution.

## System Flow

Alexa Voice Interface  
↓  
Alexa Skills Kit  
↓  
AWS Lambda  
↓  
SchoolFlow Agent  
↓  
Amazon Bedrock + Strands Agents SDK  
↓  
Candidate Ranking Tools  
↓  
Human Approval Gate  
↓  
Schedule Update  
↓  
Substitute Notification

## Core Workflow

1. A school administrator reports a teacher absence.
2. SchoolFlow evaluates available substitute candidates.
3. Candidates are ranked using:
   - schedule conflicts
   - subject match
   - school stage match
   - workload
4. SchoolFlow recommends the best safe candidate.
5. A human administrator approves or rejects the recommendation.
6. If rejected, SchoolFlow remembers the rejection and re-ranks candidates.
7. If approved, SchoolFlow updates the schedule.
8. The selected substitute receives a notification.
9. If no safe candidate remains, the case is escalated.

## Safety Principle

**AI recommends → Human approves → System executes safely**

SchoolFlow never assigns a substitute automatically without explicit human approval.
