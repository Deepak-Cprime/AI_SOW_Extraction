from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class Milestone(BaseModel):
    name: str = Field(..., description="Name of the milestone")
    description: str = Field(..., description="Detailed description of the milestone")
    due_date: Optional[str] = Field(None, description="Due date in YYYY-MM-DD format")
    payment_amount: Optional[str] = Field(None, description="Associated payment amount")

class Deliverable(BaseModel):
    name: str = Field(..., description="Name of the deliverable")
    description: str = Field(..., description="Detailed description of the deliverable")
    delivery_date: Optional[str] = Field(None, description="Delivery date in YYYY-MM-DD format")
    related_milestone: Optional[str] = Field(None, description="Associated milestone")

class PaymentTerm(BaseModel):
    payment_type: str = Field(..., description="Type of payment (milestone-based/percentage/fixed/other)")
    amount: Optional[str] = Field(None, description="Payment amount")
    currency: Optional[str] = Field(None, description="Currency code")
    percentage: Optional[str] = Field(None, description="Payment percentage")
    trigger: Optional[str] = Field(None, description="What triggers this payment")
    due_date: Optional[str] = Field(None, description="Payment due date in YYYY-MM-DD format")
    related_milestone: Optional[str] = Field(None, description="Associated milestone")
    related_deliverable: Optional[str] = Field(None, description="Associated deliverable")
    description: Optional[str] = Field(None, description="Payment description")

class ProcessingMetadata(BaseModel):
    processing_confidence: float = Field(..., description="Overall processing confidence score")
    tables_found: int = Field(default=0, description="Total tables found in document")
    milestone_tables_identified: int = Field(default=0, description="Milestone tables identified")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")
    milestones_extracted: Optional[int] = Field(default=None, description="Number of milestones extracted")
    deliverables_extracted: Optional[int] = Field(default=None, description="Number of deliverables extracted")
    extraction_method: Optional[str] = Field(default=None, description="Extraction method used")
    markdown_saved: Optional[bool] = Field(default=None, description="Whether markdown was saved")

class SOWExtractionResponse(BaseModel):
    milestones: List[Milestone] = Field(default_factory=list, description="Extracted milestones with payment info")
    deliverables: List[Deliverable] = Field(default_factory=list, description="Extracted deliverables")
    metadata: ProcessingMetadata = Field(..., description="Processing metadata and confidence scores")

