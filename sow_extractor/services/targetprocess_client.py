import httpx
import logging
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
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}?access_token={self.access_token}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                response.raise_for_status()
                result = response.json()

                logger.info(f"Successfully sent milestone '{payload['Name']}' to TargetProcess. ID: {result.get('Id')}")
                return result

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending milestone to TargetProcess: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error sending milestone to TargetProcess: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending milestone to TargetProcess: {str(e)}")
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
