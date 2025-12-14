"""
Rekindle MVP API - Performance-only pricing model
5 endpoints, manual operations, ship tonight
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional
import uuid
import json
import csv
import io
from datetime import datetime
from pathlib import Path

# Import skill loader
import sys
sys.path.append(str(Path(__file__).parent))
from rekindle_skills.loader import get_loader

app = FastAPI(title="Rekindle MVP API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple file-based storage for MVP
DATA_DIR = Path(__file__).parent / "mvp_data"
DATA_DIR.mkdir(exist_ok=True)

# Models
class Lead(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    last_contact: Optional[str] = None

class RevivalStartRequest(BaseModel):
    batch_id: str
    business_type: Optional[str] = "generic"
    sender_name: str
    company_name: str

class ReplyIngestRequest(BaseModel):
    lead_email: str
    message_text: str
    batch_id: Optional[str] = None

class BookingRequest(BaseModel):
    lead_email: str
    meeting_type: str = "discovery"  # discovery|demo|consultation

# Helper functions
def save_json(filename: str, data: dict):
    """Save data to JSON file."""
    with open(DATA_DIR / filename, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def load_json(filename: str) -> dict:
    """Load data from JSON file."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def get_batch_file(batch_id: str) -> Path:
    """Get batch data file path."""
    return DATA_DIR / f"batch_{batch_id}.json"

# 1) POST /api/mvp/leads/upload
@app.post("/api/mvp/leads/upload")
async def upload_leads(file: UploadFile = File(...)):
    """
    Upload CSV of leads. Hard limit 50 for public demo, 5000 for internal.
    Returns batch_id and counts.
    """
    # Read CSV
    contents = await file.read()
    text = contents.decode('utf-8')

    # Parse CSV
    reader = csv.DictReader(io.StringIO(text))
    leads = []
    errors = []

    for i, row in enumerate(reader, start=2):  # Line 2 = first data row
        try:
            # Validate required fields
            if not row.get('email') or not row.get('name'):
                errors.append(f"Line {i}: Missing name or email")
                continue

            lead = {
                "name": row['name'].strip(),
                "email": row['email'].strip().lower(),
                "company": row.get('company', '').strip(),
                "phone": row.get('phone', '').strip(),
                "notes": row.get('notes', '').strip(),
                "last_contact": row.get('last_contact', '').strip(),
                "uploaded_at": datetime.now().isoformat()
            }
            leads.append(lead)

        except Exception as e:
            errors.append(f"Line {i}: {str(e)}")

    # Apply hard limit (MVP: 50, can be increased with flag)
    limit = 50
    if len(leads) > limit:
        return {
            "success": False,
            "error": f"Lead limit exceeded. Maximum {limit} leads allowed in demo mode.",
            "accepted_count": 0,
            "rejected_count": len(leads)
        }

    # Create batch
    batch_id = str(uuid.uuid4())[:8]
    batch_data = {
        "batch_id": batch_id,
        "created_at": datetime.now().isoformat(),
        "total_uploaded": len(leads),
        "leads": leads,
        "errors": errors,
        "status": "uploaded"
    }

    save_json(f"batch_{batch_id}.json", batch_data)

    return {
        "success": True,
        "batch_id": batch_id,
        "accepted_count": len(leads),
        "rejected_count": len(errors),
        "errors": errors if errors else None
    }

# 2) POST /api/mvp/revival/start
@app.post("/api/mvp/revival/start")
async def start_revival(req: RevivalStartRequest):
    """
    Generate opener messages for leads in batch.
    Dry run mode outputs messages for manual sending.
    """
    # Load batch
    batch_file = get_batch_file(req.batch_id)
    if not batch_file.exists():
        raise HTTPException(status_code=404, detail="Batch not found")

    batch_data = load_json(f"batch_{req.batch_id}.json")
    leads = batch_data.get("leads", [])

    if not leads:
        raise HTTPException(status_code=400, detail="No leads in batch")

    # Load opener skill
    loader = get_loader()
    templates = loader.get_all_templates("opener_templates", req.business_type)

    if not templates:
        raise HTTPException(status_code=500, detail="No templates found for business type")

    # Generate messages
    messages = []
    for lead in leads:
        # Pick first template variant
        template = templates[0]

        # Fill placeholders
        placeholders = {
            "name": lead['name'].split()[0],  # First name
            "pain_point": "lead generation",  # Default, should come from context
            "similar_client": "a client in your industry",
            "company": lead.get('company', 'your company'),
            "months": "6",
            "metric": "cost per lead",
            "topic": "your project",
            "timeframe": "30 days",
            "property_type": "commercial space"
        }

        filled = loader.fill_template(template, placeholders)

        message = {
            "lead_email": lead['email'],
            "lead_name": lead['name'],
            "subject": filled.get('subject', ''),
            "body": filled.get('body', ''),
            "channel": "email",
            "generated_at": datetime.now().isoformat()
        }
        messages.append(message)

    # Save messages to batch
    batch_data['messages'] = messages
    batch_data['revival_started_at'] = datetime.now().isoformat()
    batch_data['sender_name'] = req.sender_name
    batch_data['company_name'] = req.company_name
    batch_data['status'] = 'revival_started'
    save_json(f"batch_{req.batch_id}.json", batch_data)

    return {
        "success": True,
        "dry_run": True,  # Always dry run for MVP
        "sent_count": 0,
        "messages_generated": len(messages),
        "sample_messages": messages[:3],  # First 3 for preview
        "instructions": "Copy these messages and send manually via your email client. Mark sent in UI."
    }

# 3) POST /api/mvp/replies/ingest
@app.post("/api/mvp/replies/ingest")
async def ingest_reply(req: ReplyIngestRequest):
    """
    Manually ingest a reply. Classifies and suggests next action.
    """
    loader = get_loader()

    # Simple keyword-based classification for MVP
    message_lower = req.message_text.lower()

    # Check for interested signals
    interested_keywords = ['yes', 'sure', 'sounds good', 'interested', 'tell me more',
                          'pricing', 'demo', 'call', 'meeting', 'send info']
    not_interested_keywords = ['no thanks', 'not interested', 'unsubscribe',
                               'stop', 'remove', 'another direction']

    if any(kw in message_lower for kw in interested_keywords):
        classification = "interested"
        confidence = 0.8
        next_action = "send_qualifier" if "pricing" not in message_lower else "send_booking"
    elif any(kw in message_lower for kw in not_interested_keywords):
        classification = "not_interested"
        confidence = 0.9
        next_action = "remove"
    else:
        classification = "unclear"
        confidence = 0.5
        next_action = "nurture"

    # Get response template
    response_data = loader.get_rule("reply_handling", f"{classification}.{next_action.split('_')[1]}")

    # Store reply
    reply_id = str(uuid.uuid4())[:8]
    reply_record = {
        "reply_id": reply_id,
        "lead_email": req.lead_email,
        "message_text": req.message_text,
        "classification": classification,
        "confidence": confidence,
        "next_action": next_action,
        "received_at": datetime.now().isoformat(),
        "batch_id": req.batch_id
    }

    # Save to replies file
    replies = load_json("replies.json")
    if "replies" not in replies:
        replies["replies"] = []
    replies["replies"].append(reply_record)
    save_json("replies.json", replies)

    return {
        "success": True,
        "classification": classification,
        "confidence": confidence,
        "next_action": next_action,
        "suggested_response": response_data.get("message", "") if response_data else None,
        "notes": f"Reply classified as {classification}. Suggested action: {next_action}"
    }

# 4) POST /api/mvp/booking/create
@app.post("/api/mvp/booking/create")
async def create_booking(req: BookingRequest):
    """
    Create booking record. Returns payload for manual booking.
    No calendar integration in MVP.
    """
    loader = get_loader()

    # Get meeting type config
    meeting_types = loader.get_rule("booking_rules", "meeting_types")
    meeting_config = meeting_types.get(req.meeting_type, meeting_types.get("discovery"))

    # Create booking record
    booking_id = str(uuid.uuid4())[:8]
    booking = {
        "booking_id": booking_id,
        "lead_email": req.lead_email,
        "meeting_type": req.meeting_type,
        "duration_minutes": meeting_config.get("duration", 15),
        "status": "needs_human_booking",
        "created_at": datetime.now().isoformat()
    }

    # Save booking
    bookings = load_json("bookings.json")
    if "bookings" not in bookings:
        bookings["bookings"] = []
    bookings["bookings"].append(booking)
    save_json("bookings.json", bookings)

    return {
        "success": True,
        "booking_id": booking_id,
        "needs_human_booking": True,
        "instructions": f"Send your Calendly link to {req.lead_email}. Meeting type: {req.meeting_type} ({meeting_config.get('duration')} min)",
        "booking_payload": booking
    }

# 5) GET /api/mvp/batches/{batch_id}/report
@app.get("/api/mvp/batches/{batch_id}/report")
async def get_batch_report(batch_id: str):
    """
    Generate performance report for batch.
    Calculate fees based on performance pricing.
    """
    # Load batch
    batch_file = get_batch_file(batch_id)
    if not batch_file.exists():
        raise HTTPException(status_code=404, detail="Batch not found")

    batch_data = load_json(f"batch_{batch_id}.json")

    # Load all replies
    all_replies = load_json("replies.json").get("replies", [])
    batch_replies = [r for r in all_replies if r.get("batch_id") == batch_id]

    # Load all bookings
    all_bookings = load_json("bookings.json").get("bookings", [])

    # Count metrics
    leads_contacted = len(batch_data.get("leads", []))
    replies_received = len(batch_replies)
    interested_count = len([r for r in batch_replies if r["classification"] == "interested"])
    qualified_count = len([r for r in batch_replies if r["next_action"] in ["send_qualifier", "send_booking"]])
    meetings_booked = len(all_bookings)  # Simplified for MVP

    # Calculate fees
    loader = get_loader()
    pricing = loader.get_rule("pricing", "performance_pricing")

    revival_fee = interested_count * pricing["revived_lead_fee"]
    booking_fee = meetings_booked * pricing["booked_meeting_fee"]
    total_fee = revival_fee + booking_fee

    # Generate CSV export data
    export_data = []
    for lead in batch_data.get("leads", []):
        lead_reply = next((r for r in batch_replies if r["lead_email"] == lead["email"]), None)
        export_data.append({
            "name": lead["name"],
            "email": lead["email"],
            "company": lead.get("company", ""),
            "replied": "Yes" if lead_reply else "No",
            "classification": lead_reply["classification"] if lead_reply else "no_reply",
            "status": lead_reply["next_action"] if lead_reply else "pending"
        })

    return {
        "success": True,
        "batch_id": batch_id,
        "report": {
            "leads_contacted": leads_contacted,
            "replies_received": replies_received,
            "interested_count": interested_count,
            "qualified_count": qualified_count,
            "meetings_booked": meetings_booked,
            "revival_fee_gbp": round(revival_fee, 2),
            "booking_fee_gbp": round(booking_fee, 2),
            "total_fee_gbp": round(total_fee, 2)
        },
        "export_data": export_data
    }

@app.get("/")
async def root():
    return {
        "service": "Rekindle MVP API",
        "version": "0.1.0",
        "pricing": "£0 upfront, £25 per booked meeting, £0.10 per revived lead",
        "endpoints": [
            "POST /api/mvp/leads/upload",
            "POST /api/mvp/revival/start",
            "POST /api/mvp/replies/ingest",
            "POST /api/mvp/booking/create",
            "GET /api/mvp/batches/{batch_id}/report"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
