"""Canvas API client for interacting with Canvas LMS."""

import os
from typing import Dict, List, Any, Optional
import httpx
from datetime import datetime, timedelta


class CanvasAPI:
    """Canvas API client for Stanford Canvas."""

    def __init__(self, base_url: str = "https://canvas.stanford.edu", api_token: Optional[str] = None):
        self.base_url = base_url
        self.api_token = api_token or os.getenv("CANVAS_API_TOKEN")

        if not self.api_token:
            raise ValueError("Canvas API token is required. Set CANVAS_API_TOKEN environment variable.")

        self.client = httpx.AsyncClient(timeout=30.0)

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make an authenticated GET request to the Canvas API."""
        url = f"{self.base_url}/api/v1{endpoint}"
        if params is None:
            params = {}
        params["access_token"] = self.api_token

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Canvas API request failed: {e}")

    async def _make_post(self, endpoint: str, payload: Dict[str, Any]) -> Any:
        """Make an authenticated POST request to the Canvas API."""
        url = f"{self.base_url}/api/v1{endpoint}"
        params = {"access_token": self.api_token}

        try:
            response = await self.client.post(url, params=params, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"Canvas API POST failed: {e}")

    # ──────────────────────────────────────────────
    # Original tools (unchanged)
    # ──────────────────────────────────────────────

    async def get_user_profile(self) -> Dict[str, Any]:
        return await self._make_request("/users/self")

    async def get_courses(self, enrollment_state: str = "active") -> List[Dict[str, Any]]:
        params = {"enrollment_state": enrollment_state}
        courses = await self._make_request("/courses", params)
        active_courses = []
        for course in courses:
            enrollments = course.get("enrollments", [])
            if enrollments and enrollments[0].get("enrollment_state") == "active":
                active_courses.append(course)
        return active_courses

    async def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        events = await self._make_request("/users/self/upcoming_events")
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        upcoming = []
        for event in events:
            date_str = None
            if event.get("assignment", {}).get("due_at"):
                date_str = event["assignment"]["due_at"]
            elif event.get("start_at"):
                date_str = event["start_at"]
            if date_str:
                try:
                    event_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    if event_date <= cutoff_date and (event.get("assignment") or event.get("type") == "assignment"):
                        upcoming.append(event)
                except ValueError:
                    continue
        return upcoming

    async def get_course_assignments(self, course_id: str) -> List[Dict[str, Any]]:
        return await self._make_request(f"/courses/{course_id}/assignments")

    async def get_todo_items(self) -> List[Dict[str, Any]]:
        return await self._make_request("/users/self/todo")

    async def get_assignment_details(self, course_id: str, assignment_id: str) -> Dict[str, Any]:
        return await self._make_request(f"/courses/{course_id}/assignments/{assignment_id}")

    async def get_grades(self, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if course_id:
            return await self._make_request(f"/courses/{course_id}/assignments", {"include": ["submission"]})
        return await self._make_request("/users/self/enrollments",
                                        {"include": ["current_grading_period_scores", "total_scores"]})

    async def get_calendar_events(self, start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"type": "event"}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self._make_request("/calendar_events", params)

    async def get_announcements(self, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if course_id:
            return await self._make_request(f"/courses/{course_id}/discussion_topics",
                                            {"only_announcements": "true"})
        return await self._make_request("/announcements")

    async def get_course_modules(self, course_id: str) -> List[Dict[str, Any]]:
        return await self._make_request(f"/courses/{course_id}/modules",
                                        {"include": ["items", "content_details"]})

    async def get_course_activity_stream(self) -> List[Dict[str, Any]]:
        return await self._make_request("/users/self/activity_stream")

    # ──────────────────────────────────────────────
    # New tools: syllabus, pages, module items, files, submissions
    # ──────────────────────────────────────────────

    async def get_syllabus(self, course_id: str) -> Dict[str, Any]:
        """Get the syllabus body for a course."""
        return await self._make_request(f"/courses/{course_id}",
                                        {"include[]": "syllabus_body"})

    async def get_course_pages(self, course_id: str) -> List[Dict[str, Any]]:
        """List all wiki pages in a course."""
        return await self._make_request(f"/courses/{course_id}/pages",
                                        {"per_page": 100, "sort": "updated_at", "order": "desc"})

    async def get_page_content(self, course_id: str, page_url: str) -> Dict[str, Any]:
        """Get the full HTML body of a specific Canvas page."""
        return await self._make_request(f"/courses/{course_id}/pages/{page_url}")

    async def get_module_items(self, course_id: str, module_id: str) -> List[Dict[str, Any]]:
        """Get all items inside a module, including external URLs and page links."""
        return await self._make_request(
            f"/courses/{course_id}/modules/{module_id}/items",
            {"include[]": "content_details", "per_page": 100}
        )

    async def get_course_files(self, course_id: str) -> List[Dict[str, Any]]:
        """List all files in a course with their download URLs."""
        return await self._make_request(f"/courses/{course_id}/files",
                                        {"per_page": 100, "sort": "updated_at", "order": "desc"})

    async def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """Get metadata and download URL for a specific file."""
        return await self._make_request(f"/files/{file_id}")

    async def get_discussion_topics(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all discussion topics (not announcements) for a course."""
        return await self._make_request(f"/courses/{course_id}/discussion_topics")

    async def get_submission_status(self, course_id: str, assignment_id: str) -> Dict[str, Any]:
        """Check whether the current user has submitted a given assignment."""
        return await self._make_request(
            f"/courses/{course_id}/assignments/{assignment_id}/submissions/self"
        )

    async def close(self):
        await self.client.aclose()
