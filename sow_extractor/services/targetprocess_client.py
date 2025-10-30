import httpx
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
from sow_extractor.core.config import get_settings

logger = logging.getLogger(__name__)

class TargetProcessClient:
    """Client for sending milestone data to TargetProcess"""

    def __init__(self):
        self.settings = get_settings()
        self.domain = self.settings.targetprocess_domain
        self.access_token = self.settings.targetprocess_access_token

        if not self.domain or not self.access_token:
            logger.warning("TargetProcess credentials not configured. Milestone sync will be skipped.")

        self.api_url = f"{self.domain}/api/v1/KeyMilestones"

    async def send_milestone(self, milestone: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a single milestone to TargetProcess

        Args:
            milestone: Dictionary containing milestone data with keys:
                - name: Milestone name
                - description: Milestone description
                - due_date: Due date (Date field in TargetProcess)
                - payment_amount: Payment amount

        Returns:
            Response from TargetProcess API or None if credentials not configured
        """
        if not self.domain or not self.access_token:
            logger.info("Skipping milestone sync - TargetProcess not configured")
            return None

        # Prepare payload matching TargetProcess API format
        payload = {
            "Name": milestone.get("name", ""),
            "Description": milestone.get("description", ""),
            "Date": milestone.get("due_date", ""),
            "Payment": milestone.get("payment_amount", ""),
            "SOW": True
        }

        try:
            url = f"{self.api_url}?access_token={self.access_token}"
            logger.info(f"Sending milestone to TargetProcess: {url}")
            logger.debug(f"Payload: {payload}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                # Log response details
                logger.info(f"TargetProcess response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                logger.debug(f"Response body: {response.text[:500]}")  # First 500 chars

                # Check if response is successful
                response.raise_for_status()

                # Handle empty response
                if not response.text or response.text.strip() == "":
                    logger.warning("TargetProcess returned empty response")
                    return {"status": "created", "message": "Empty response from TargetProcess"}

                # TargetProcess returns XML by default, parse it
                try:
                    # Parse XML response
                    root = ET.fromstring(response.text)

                    # Extract key fields from XML
                    milestone_id = root.get('Id')
                    milestone_name = root.get('Name')

                    # Extract custom fields
                    custom_fields = {}
                    custom_fields_elem = root.find('CustomFields')
                    if custom_fields_elem is not None:
                        for field in custom_fields_elem.findall('Field'):
                            field_name = field.find('Name')
                            field_value = field.find('Value')
                            if field_name is not None and field_value is not None:
                                custom_fields[field_name.text] = field_value.text

                    result = {
                        "Id": milestone_id,
                        "Name": milestone_name,
                        "Description": root.findtext('Description', ''),
                        "CreateDate": root.findtext('CreateDate', ''),
                        "ModifyDate": root.findtext('ModifyDate', ''),
                        "CustomFields": custom_fields,
                        "status": "created"
                    }

                    logger.info(f"Successfully sent milestone '{payload['Name']}' to TargetProcess. ID: {milestone_id}")
                    return result

                except ET.ParseError as xml_err:
                    logger.error(f"Failed to parse XML response: {xml_err}")
                    logger.error(f"Response text: {response.text[:500]}")
                    return {"status": "error", "message": "Failed to parse XML response", "response_text": response.text[:500]}

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending milestone to TargetProcess: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error sending milestone to TargetProcess: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending milestone to TargetProcess: {str(e)}")
            logger.exception("Full traceback:")
            raise

    async def send_milestones_batch(self, milestones: List[Dict[str, Any]]) -> List[Optional[Dict[str, Any]]]:
        """
        Send multiple milestones to TargetProcess

        Args:
            milestones: List of milestone dictionaries

        Returns:
            List of responses from TargetProcess API
        """
        if not self.domain or not self.access_token:
            logger.info("Skipping milestone batch sync - TargetProcess not configured")
            return []

        results = []
        for milestone in milestones:
            try:
                result = await self.send_milestone(milestone)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to send milestone '{milestone.get('name')}': {str(e)}")
                results.append(None)

        success_count = sum(1 for r in results if r is not None)
        logger.info(f"Sent {success_count}/{len(milestones)} milestones to TargetProcess")

        return results
