# SchoolFlow – Friction Log

This friction log documents real development challenges encountered while building SchoolFlow for the Amazon Developer Hackathon.

## 1. Bedrock credentials and model access

**Expected:**  
The SchoolFlow agent should connect to Amazon Bedrock and invoke the selected model.

**What happened:**  
Initial agent runs failed with AWS credential and model-access errors, including missing credentials and account/model access configuration issues.

**Workaround / Fix:**  
Configured the AWS account correctly, enabled the required Bedrock model access, and later moved execution into AWS Lambda using the Lambda execution role instead of storing API keys in source code.

**Suggested improvement:**  
Provide a clearer end-to-end onboarding checklist for Bedrock access, model permissions, IAM roles, and first successful invocation.

---

## 2. Alexa approve/reject intent matching

**Expected:**  
Commands such as “approve Sara” and “reject Sara” should consistently trigger the correct intent.

**What happened:**  
Some approval and rejection phrases were initially not recognized correctly by the Alexa interaction model.

**Workaround / Fix:**  
Added explicit sample utterances and separated the decision flow so approval and rejection could be handled reliably.

**Suggested improvement:**  
Provide clearer simulator diagnostics explaining why an utterance matched or failed to match a specific intent.

---

## 3. Rejected candidate memory

**Expected:**  
After an administrator rejects a candidate, that teacher should not be recommended again in the same workflow.

**What happened:**  
The first version could recommend a previously rejected teacher again.

**Workaround / Fix:**  
Added rejected candidate state to the workflow and carried it through Alexa session attributes. The ranking logic now excludes rejected candidates before re-ranking.

**Suggested improvement:**  
More examples of stateful human-in-the-loop agent workflows would help developers implement this pattern faster.

---

## 4. Connecting Alexa, Lambda, and the SchoolFlow agent

**Expected:**  
Alexa should invoke Lambda, which should call the SchoolFlow agent and complete the workflow end to end.

**What happened:**  
The first working Alexa version contained substitute-selection logic directly inside Lambda, while the Strands agent existed separately.

**Workaround / Fix:**  
Refactored the project to expose a single `run_schoolflow()` entry point from `schoolflow_agent.py`, then connected `lambda_function.py` to that agent workflow.

**Suggested improvement:**  
Provide more complete examples showing Alexa + Lambda + Bedrock + agent orchestration in one reference architecture.

---

## 5. Lambda deployment dependencies

**Expected:**  
Uploading the Python source files should be enough to run the function.

**What happened:**  
Lambda also required the Strands Agents SDK and its dependencies, which were not included automatically.

**Workaround / Fix:**  
Built a deployment ZIP containing:
- `lambda_function.py`
- `schoolflow_agent.py`
- `strands-agents`
- required Python dependencies

The package was built in Google Colab and uploaded to Lambda.

**Suggested improvement:**  
Provide simpler guidance for packaging agent SDK dependencies for Lambda.

---

## 6. Python runtime compatibility

**Expected:**  
The deployment package should work with the Lambda runtime.

**What happened:**  
The Lambda function was initially using Python 3.14, while the deployment package had been built with Python 3.13.

**Workaround / Fix:**  
Changed the Lambda runtime to Python 3.13 and kept the architecture as `x86_64`.

**Suggested improvement:**  
Surface clearer compatibility warnings when uploaded native dependencies were built for a different Python runtime.

---

## 7. Lambda timeout

**Expected:**  
The default Lambda timeout would be sufficient.

**What happened:**  
The default timeout was only 3 seconds, which is too short for an agent workflow that may invoke Amazon Bedrock.

**Workaround / Fix:**  
Increased the Lambda timeout to 30 seconds before testing the full workflow.

**Suggested improvement:**  
Agentic Lambda templates could recommend more realistic timeout defaults for model inference workloads.

---

# Result

After resolving these issues, the full SchoolFlow workflow was successfully tested through the Alexa Simulator:

**Teacher absence → Recommendation → Human rejection → Re-ranking → Human approval → Schedule update → Notification**

The final architecture keeps the human administrator in control while using AI and deterministic rules to make the process faster and safer.
