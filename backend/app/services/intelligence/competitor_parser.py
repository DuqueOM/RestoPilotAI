"""
Competitor Parser Service - Multimodal parsing of mixed competitor inputs.
"""

from typing import Any, Dict, List, Optional
import json
from loguru import logger
from google.genai import types
from app.services.gemini.base_agent import GeminiAgent

class CompetitorParser:
    """
    Parses mixed competitor inputs (text notes, files, links) using Gemini 3.
    Identifies distinct competitors and extracts structured profiles.
    """

    def __init__(self, agent: GeminiAgent):
        self.agent = agent

    async def parse_mixed_input(
        self, 
        text_input: Optional[str] = None, 
        files: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Parse mixed input to identify and extract competitors.

        Args:
            text_input: User notes, links, descriptions.
            files: List of dicts with 'content' (bytes), 'mime_type', 'filename'.

        Returns:
            List of competitor profiles.
        """
        if not text_input and not files:
            return []

        logger.info("Parsing mixed competitor input...")

        # Prepare multimodal content for Gemini
        contents = []
        
        # 1. Add Text
        prompt_text = """You are a Competitor Intelligence Expert.
Your task is to analyze the provided unstructured information (notes, files, images, menus) and extracting a CLEAN, STRUCTURED list of competitors.

INPUTS:
The user has provided a mix of:
- Notes/Links (Text)
- Files (Menus, Photos, Videos, PDFs)

YOUR GOAL:
1. IDENTIFY: How many distinct competitors are mentioned?
2. SEPARATE: Assign each piece of info (or insight from it) to the correct competitor.
3. EXTRACT: Create a profile for each.

STRUCTURE PER COMPETITOR:
- name: Business name
- website: URL if found
- location: Address or city if found
- social_handles: Instagram/TikTok/FB
- identified_from: List of filenames or "text_notes" that contributed to this profile
- key_insights: What did we learn? (e.g. "Has a strong brunch menu", "Uses red decor")
- menu_summary: Brief summary of their offering if visible

NOTES:
- If a file is a menu, extract the restaurant name from it.
- If a file is a photo, determine if it belongs to a competitor mentioned in text or a new one.
- If text contains a list of links, each link is likely a competitor.

RESPONSE FORMAT (JSON):
{
  "competitors": [
    {
      "name": "...",
      "website": "...",
      "location": "...",
      "social_handles": ["..."],
      "identified_from": ["file1.pdf", "text_notes"],
      "key_insights": ["..."],
      "menu_summary": "..."
    }
  ],
  "summary": "Found X competitors..."
}
"""
        
        contents.append(types.Content(parts=[types.Part(text=prompt_text)]))
        
        if text_input:
            contents[0].parts.append(types.Part(text=f"\n\n--- USER TEXT NOTES ---\n{text_input}"))

        # 2. Add Files
        if files:
            for i, file in enumerate(files):
                try:
                    mime = file.get("mime_type", "application/octet-stream")
                    data = file.get("content")
                    filename = file.get("filename", f"file_{i}")
                    
                    # Log file processing
                    logger.debug(f"Adding file to prompt: {filename} ({mime})")
                    
                    # Add file marker in text
                    contents[0].parts.append(types.Part(text=f"\n\n--- FILE: {filename} ({mime}) ---"))
                    
                    # Add blob
                    contents[0].parts.append(
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime,
                                data=data
                            )
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to attach file {file.get('filename')}: {e}")

        # Call Gemini
        try:
            response = self.agent.client.models.generate_content(
                model=self.agent.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.2, # Low temp for extraction
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON
            result = json.loads(response.text)
            competitors = result.get("competitors", [])
            logger.info(f"Extracted {len(competitors)} competitors from mixed input.")
            return competitors

        except Exception as e:
            logger.error(f"Competitor parsing failed: {e}")
            return []
