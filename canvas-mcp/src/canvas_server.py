#!/usr/bin/env python3
"""Canvas MCP Server - Provides Canvas LMS integration for Claude Desktop."""

import asyncio
import json
import os
import sys
from typing import Any
from dotenv import load_dotenv

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from canvas_api import CanvasAPI

load_dotenv()


class CanvasMCPServer:

    def __init__(self):
        self.server = Server("canvas-mcp-server")
        self.canvas_api = None

    async def initialize_canvas_api(self):
        try:
            self.canvas_api = CanvasAPI()
            await self.canvas_api.get_user_profile()
            print("✅ Canvas API connection successful", file=sys.stderr)
        except Exception as e:
            print(f"❌ Failed to connect to Canvas API: {e}", file=sys.stderr)
            raise

    def setup_handlers(self):

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return [
                # ── Original tools ──────────────────────────────────────────
                types.Tool(
                    name="get_courses",
                    description="Get all active Canvas courses for the user",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                types.Tool(
                    name="get_upcoming_assignments",
                    description="Get upcoming assignments and deadlines",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "days_ahead": {
                                "type": "number",
                                "description": "Number of days to look ahead (default: 30)",
                                "default": 30,
                            }
                        },
                        "required": [],
                    },
                ),
                types.Tool(
                    name="get_course_assignments",
                    description="Get all assignments for a specific course",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"}
                        },
                        "required": ["course_id"],
                    },
                ),
                types.Tool(
                    name="get_todo_items",
                    description="Get items from Canvas To-Do list",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                types.Tool(
                    name="get_assignment_details",
                    description="Get detailed information about a specific assignment",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"},
                            "assignment_id": {"type": "string", "description": "Canvas assignment ID"},
                        },
                        "required": ["course_id", "assignment_id"],
                    },
                ),
                types.Tool(
                    name="get_grades",
                    description="Get grades for all courses or a specific course",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID (optional)"}
                        },
                        "required": [],
                    },
                ),
                types.Tool(
                    name="get_calendar_events",
                    description="Get calendar events within a date range",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "description": "Start date ISO format (optional)"},
                            "end_date": {"type": "string", "description": "End date ISO format (optional)"},
                        },
                        "required": [],
                    },
                ),
                types.Tool(
                    name="get_announcements",
                    description="Get announcements for a course or all courses",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID (optional)"}
                        },
                        "required": [],
                    },
                ),
                types.Tool(
                    name="get_course_modules",
                    description="Get all modules for a course, including their items and content details",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"}
                        },
                        "required": ["course_id"],
                    },
                ),
                types.Tool(
                    name="get_course_activity_stream",
                    description="Get recent activity across all courses",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),

                # ── New tools ────────────────────────────────────────────────
                types.Tool(
                    name="get_syllabus",
                    description=(
                        "Get the full syllabus text for a course. Use this to understand "
                        "the weekly schedule, required readings, and grading breakdown."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"}
                        },
                        "required": ["course_id"],
                    },
                ),
                types.Tool(
                    name="get_course_pages",
                    description=(
                        "List all wiki/content pages in a course. Each page may contain "
                        "readings, lecture notes, or resource links."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"}
                        },
                        "required": ["course_id"],
                    },
                ),
                types.Tool(
                    name="get_page_content",
                    description=(
                        "Get the full HTML/text body of a specific Canvas page. "
                        "Use the page's url slug (from get_course_pages)."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"},
                            "page_url": {
                                "type": "string",
                                "description": "Page URL slug (the 'url' field from get_course_pages)",
                            },
                        },
                        "required": ["course_id", "page_url"],
                    },
                ),
                types.Tool(
                    name="get_module_items",
                    description=(
                        "Get all items inside a specific module. Items include pages, "
                        "external URLs, files, assignments, and quizzes. "
                        "Use get_course_modules first to get module IDs."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"},
                            "module_id": {"type": "string", "description": "Canvas module ID"},
                        },
                        "required": ["course_id", "module_id"],
                    },
                ),
                types.Tool(
                    name="get_course_files",
                    description=(
                        "List all files uploaded to a course (PDFs, slides, etc.) "
                        "with their download URLs."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"}
                        },
                        "required": ["course_id"],
                    },
                ),
                types.Tool(
                    name="get_file_info",
                    description="Get metadata and download URL for a specific Canvas file by file ID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {"type": "string", "description": "Canvas file ID"}
                        },
                        "required": ["file_id"],
                    },
                ),
                types.Tool(
                    name="get_discussion_topics",
                    description="Get all discussion topics (not announcements) for a course.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"}
                        },
                        "required": ["course_id"],
                    },
                ),
                types.Tool(
                    name="get_submission_status",
                    description=(
                        "Check whether you have already submitted a given assignment. "
                        "Returns submission details including submitted_at, grade, and body."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "course_id": {"type": "string", "description": "Canvas course ID"},
                            "assignment_id": {"type": "string", "description": "Canvas assignment ID"},
                        },
                        "required": ["course_id", "assignment_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            if not self.canvas_api:
                raise RuntimeError("Canvas API not initialized")

            try:
                args = arguments or {}

                # ── Original tools ──────────────────────────────────────────
                if name == "get_courses":
                    result = await self.canvas_api.get_courses()

                elif name == "get_upcoming_assignments":
                    result = await self.canvas_api.get_upcoming_events(args.get("days_ahead", 30))

                elif name == "get_course_assignments":
                    result = await self.canvas_api.get_course_assignments(args["course_id"])

                elif name == "get_todo_items":
                    result = await self.canvas_api.get_todo_items()

                elif name == "get_assignment_details":
                    result = await self.canvas_api.get_assignment_details(
                        args["course_id"], args["assignment_id"]
                    )

                elif name == "get_grades":
                    result = await self.canvas_api.get_grades(args.get("course_id"))

                elif name == "get_calendar_events":
                    result = await self.canvas_api.get_calendar_events(
                        args.get("start_date"), args.get("end_date")
                    )

                elif name == "get_announcements":
                    result = await self.canvas_api.get_announcements(args.get("course_id"))

                elif name == "get_course_modules":
                    result = await self.canvas_api.get_course_modules(args["course_id"])

                elif name == "get_course_activity_stream":
                    result = await self.canvas_api.get_course_activity_stream()

                # ── New tools ────────────────────────────────────────────────
                elif name == "get_syllabus":
                    result = await self.canvas_api.get_syllabus(args["course_id"])

                elif name == "get_course_pages":
                    result = await self.canvas_api.get_course_pages(args["course_id"])

                elif name == "get_page_content":
                    result = await self.canvas_api.get_page_content(
                        args["course_id"], args["page_url"]
                    )

                elif name == "get_module_items":
                    result = await self.canvas_api.get_module_items(
                        args["course_id"], args["module_id"]
                    )

                elif name == "get_course_files":
                    result = await self.canvas_api.get_course_files(args["course_id"])

                elif name == "get_file_info":
                    result = await self.canvas_api.get_file_info(args["file_id"])

                elif name == "get_discussion_topics":
                    result = await self.canvas_api.get_discussion_topics(args["course_id"])

                elif name == "get_submission_status":
                    result = await self.canvas_api.get_submission_status(
                        args["course_id"], args["assignment_id"]
                    )

                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [types.TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    canvas_server = CanvasMCPServer()
    canvas_server.setup_handlers()
    await canvas_server.initialize_canvas_api()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        print("🚀 Canvas MCP Server started", file=sys.stderr)
        await canvas_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="canvas-mcp-server",
                server_version="0.2.0",
                capabilities=canvas_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
