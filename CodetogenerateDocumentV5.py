import json
import re
from googleapiclient.discovery import build
from google.oauth2 import service_account
import google.generativeai as genai

# Set your API key
genai.configure(api_key='Enter Key Here')

# Initialize the generative model
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Collect user inputs
user_input = {
    "client_name": input("Enter the Client Name: "),
    "project_name": input("Enter the Project Name: "),
    "hackett_pm": input("Enter the Hackett Project Manager: "),
    "project_number": input("Enter the Project Number: "),
    "hackett_requestor": input("Enter the Hackett Requestor: "),
    "project_phase": input("Enter the Project Phase: "),
    "description_change": input("Enter the Change Request Description: "),
    "cost": input("Enter the Cost (e.g., 10,000 USD): "),
    "priority": input("Enter the Priority (e.g., High): ")
}

# Define the JSON schema as a string
schema_text = """
{
    "type": "object",
    "properties": {
        "user_input": {
            "type": "object",
            "properties": {
                "client_name": {"type": "string"},
                "project_name": {"type": "string"},
                "hackett_pm": {"type": "string"},
                "project_number": {"type": "string"},
                "hackett_requestor": {"type": "string"},
                "project_phase": {"type": "string"},
                "description_change": {"type": "string"},
                "cost": {"type": "string"},
                "priority": {"type": "string"}
            }
        },
        "ai_generated_response": {
            "type": "object",
            "properties": {
                "specific_change": {"type": "string"},
                "impact_of_change": {"type": "string"},
                "justification": {"type": "string"},
                "resource_allocation": {"type": "string"},
                "timeline": {"type": "string"}
            }
        }
    }
}
"""

# **One-Shot Prompting**: Example-Based Training + User Input
prompt = f"""
You are an AI expert in Human Capital Management (HCM) implementations. Your task is to generate a **structured change request** based on both **user-provided data** and **your trained knowledge of best practices**.

### **Example: HCM Change Request for Payroll Integration**
#### **User Input:**
{{
    "client_name": "ABC Corp",
    "project_name": "Payroll Automation",
    "hackett_pm": "John Doe",
    "project_number": "HR-2024-01",
    "hackett_requestor": "Jane Smith",
    "project_phase": "Implementation",
    "description_change": "We need to integrate Oracle HCM with ADP Payroll for automated payroll processing.",
    "cost": "15,000 USD",
    "priority": "High"
}}

#### **AI-Generated Response:**
{{
    "specific_change": "Develop an integration between Oracle HCM and ADP Payroll using REST APIs.\\nMap employee compensation data fields (e.g., base salary, bonuses, deductions).\\nImplement a scheduled batch job for payroll data transfer.",
    "impact_of_change": "Requires data validation to ensure payroll accuracy.\\nPotential delays in payroll processing if integration fails.\\nCompliance risks if tax calculations are not mapped correctly.",
    "justification": "This integration will eliminate manual data entry, reducing payroll errors and improving efficiency.",
    "resource_allocation": "2 Integration Developers, 1 Payroll Specialist, 1 QA Engineer.",
    "timeline": "4 weeks - 2 weeks for development, 1 week for testing, 1 week for UAT."
}}

---

### **Now, Generate a Response Based on the Following User Input:**
#### **User Input:**
{json.dumps(user_input, indent=4)}

---

### **Response Format:**
Ensure the output follows this JSON schema:
{schema_text}
"""

# Generate structured content using the generative model
result= model.generate_content(prompt)
print (result)

# Service Account Key (Replace with your actual credentials)
SERVICE_ACCOUNT_KEY = {
   "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCT/zyZlR9eSjkD\n...",
  "client_email": "",
  "client_id": "",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",
  "universe_domain": "googleapis.com"
}

# Convert the key to a credentials object
credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_KEY)


docs_service = build("docs", "v1", credentials=credentials)
drive_service = build("drive", "v3", credentials=credentials)

# Replace with your Google Docs Template ID
TEMPLATE_DOCUMENT_ID = "1CLgZeB_sfH6ylxFN4d2Nd7VjnwPYpo3wdinFbXZMHdw"  # Replace with actual ID

# Create a copy of the template
new_document = drive_service.files().copy(
    fileId=TEMPLATE_DOCUMENT_ID, body={"name": "Change Request - Station Casinos"}
).execute()
new_document_id = new_document["id"]

# AI-Generated Content (Replace these values dynamically)
# Parsing Logic
def parse_ai_response(result):
    """Parses AI-generated response and extracts a valid JSON object"""
    try:
        ai_response_text = result.text.strip()  # Remove leading/trailing whitespace
        
        # Debug: Print raw AI response for inspection
        print("🔍 Raw AI Response:", ai_response_text)

        # Extract JSON part if wrapped in a code block (```json ... ```)
        json_match = re.search(r'```json\s*(.*?)\s*```', ai_response_text, re.DOTALL)
        if json_match:
            ai_response_text = json_match.group(1)  # Extract only the JSON content

        # Convert to dictionary safely
        ai_response_json = json.loads(ai_response_text)

    except json.JSONDecodeError as e:
        print(f"⚠️ Error: AI response is not valid JSON. Details: {str(e)}")
        ai_response_json = {}  # Fallback to empty dictionary

    return ai_response_json  # Return parsed JSON dictionary

ai_response_json = parse_ai_response(result)

if ai_response_json:
    print("✅ Successfully parsed AI response:")
    print(json.dumps(ai_response_json, indent=4))  # Pretty-print JSON
else:
    print("❌ Failed to parse AI response.")


# Extract values dynamically from AI response
ai_output = {
    "client_name": user_input.get("client_name", ""),
    "project_name": user_input.get("project_name", ""),
    "hackett_pm": user_input.get("hackett_pm", ""),
    "project_number": user_input.get("project_number", ""),
    "hackett_requestor": user_input.get("hackett_requestor", ""),
    "project_phase": user_input.get("project_phase", ""),
    "description_change": user_input.get("description_change", ""),
    "cost": user_input.get("cost", ""),
    "priority": user_input.get("priority", ""),
    "specific_change": ai_response_json.get("ai_generated_response", {}).get("specific_change", ""),
    "impact_of_change": ai_response_json.get("ai_generated_response", {}).get("impact_of_change", ""),
    "justification": ai_response_json.get("ai_generated_response", {}).get("justification", ""),
    "resource_allocation": ai_response_json.get("ai_generated_response", {}).get("resource_allocation", ""),
    "timeline": ai_response_json.get("ai_generated_response", {}).get("timeline", ""),
}


# Replace placeholders in Google Docs
requests = [
    {
        "replaceAllText": {
            "containsText": {"text": f"{{{{{key}}}}}", "matchCase": True},
            "replaceText": value,
        }
    }
    for key, value in ai_output.items()
]

docs_service.documents().batchUpdate(documentId=new_document_id, body={"requests": requests}).execute()

# Grant write access to the user
PERMISSION = {
    "type": "user",
    "role": "writer",
    "emailAddress": "ritwick.durgapur@gmail.com",
}

drive_service.permissions().create(fileId=new_document_id, body=PERMISSION).execute()

print(f"✅ Document successfully created and shared: https://docs.google.com/document/d/{new_document_id}/edit")