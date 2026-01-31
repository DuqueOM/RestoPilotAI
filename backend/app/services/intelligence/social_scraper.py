import asyncio
import concurrent.futures
from datetime import datetime
from typing import List, Optional

import instaloader
from loguru import logger
from pydantic import BaseModel


class SocialPost(BaseModel):
    id: str
    shortcode: str
    url: str
    caption: str
    likes: int
    comments: int
    timestamp: datetime
    is_video: bool
    image_url: str
    typename: str


class SocialProfile(BaseModel):
    username: str
    full_name: str
    biography: str
    followers: int
    following: int
    posts_count: int
    is_verified: bool
    profile_pic_url: str


class SocialScraper:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    async def get_profile(self, username: str) -> Optional[SocialProfile]:
        """Get basic profile information."""
        try:
            loop = asyncio.get_event_loop()
            profile = await loop.run_in_executor(
                self.executor,
                lambda: instaloader.Profile.from_username(self.L.context, username),
            )

            return SocialProfile(
                username=profile.username,
                full_name=profile.full_name,
                biography=profile.biography,
                followers=profile.followers,
                following=profile.followees,
                posts_count=profile.mediacount,
                is_verified=profile.is_verified,
                profile_pic_url=profile.profile_pic_url,
            )
        except Exception as e:
            logger.error(f"Error scraping profile {username}: {e}")
            return None

    async def get_recent_posts(self, username: str, limit: int = 5) -> List[SocialPost]:
        """Get recent posts from a public profile."""
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.executor, self._sync_get_posts, username, limit
            )
        except Exception as e:
            logger.error(f"Error scraping posts for {username}: {e}")
            return []

    def _sync_get_posts(self, username: str, limit: int) -> List[SocialPost]:
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            posts = []
            count = 0
            for post in profile.get_posts():
                if count >= limit:
                    break

                posts.append(
                    SocialPost(
                        id=str(post.mediaid),
                        shortcode=post.shortcode,
                        url=f"https://www.instagram.com/p/{post.shortcode}/",
                        caption=post.caption or "",
                        likes=post.likes,
                        comments=post.comments,
                        timestamp=post.date_local,
                        is_video=post.is_video,
                        image_url=post.url,
                        typename=post.typename,
                    )
                )
                count += 1
            return posts
        except Exception as e:
            logger.error(f"Sync scrape error for {username}: {e}")
            return []

    async def search_username(self, query: str) -> Optional[str]:
        """
        Attempt to find an instagram username based on a query (e.g. restaurant name).
        This is a heuristic/best-effort search.
        """
        # Instaloader doesn't have a direct search without login usually,
        # but we can try to guess or use search iterator if logged in.
        # For now, we return None as search usually requires login.
        # We could implement a google search fallback here.
        return None
