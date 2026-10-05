# SchoolFlow Voice Agent

SchoolFlow is a voice-first AI agent for safe teacher absence and substitute management.

## Problem

When a teacher is absent, school administrators often need to quickly identify a suitable substitute, check conflicts, compare workload, make a decision, update the schedule, and notify the selected teacher.

This process is often manual, repetitive, and time-sensitive.

## Solution

SchoolFlow turns this process into a safe agentic workflow:

**Teacher Absence → Candidate Ranking → Human Approval → Schedule Update → Notification**

The AI recommends, but the human remains in control.

## Demo Scenario

1. Nora is absent on Sunday during period 2.
2. SchoolFlow recommends Sara.
3. The administrator rejects Sara.
4. SchoolFlow remembers the rejection and recommends Huda.
5. The administrator approves Huda.
6. The schedule is updated.
7. Huda receives the assignment notification.

## Core Principle

**AI recommends → Human approves → System executes safely**

## Technology Stack

- Alexa Skills Kit
- AWS Lambda
- Amazon Bedrock
- Strands Agents SDK
- Python
- Human-in-the-loop approval
- Agentic workflow orchestration

## Architecture

Alexa Voice Interface  
↓  
AWS Lambda  
↓  
SchoolFlow Agent  
↓  
Candidate Ranking  
↓  
Human Approval  
↓  
Schedule Update  
↓  
Notification

## Safety

SchoolFlow does not automatically assign a substitute without human approval.

Rejected candidates are remembered during the workflow and excluded from subsequent recommendations.

If no safe substitute remains, the case is escalated to the school administrator.

## Status

Current prototype supports:

- Teacher absence detection
- Substitute recommendation
- Conflict and workload-aware ranking
- Human approval and rejection
- Re-ranking after rejection
- Escalation
- Schedule update
- Substitute notification
- Alexa voice interaction

## Hackathon

Built for Amazon Build, Ship, Shape 2026.

## Author

Dr. Zahra Al-Ansari
