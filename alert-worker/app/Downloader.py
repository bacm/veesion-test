import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncFileDownloader:
    def __init__(self, max_concurrent: int = 5, chunk_size: int = 8192):
        self.chunk_size = chunk_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_file(
        self, 
        session: aiohttp.ClientSession, 
        url: str, 
        filepath: Path,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """Download a single file with progress tracking"""
        async with self.semaphore:  # Limit concurrent downloads
            try:
                logger.info(f"Starting download: {url}")
                
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download {url}: HTTP {response.status}")
                        return False
                    
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    
                    # Create directory if it doesn't exist
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    
                    async with aiofiles.open(filepath, 'wb') as file:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            await file.write(chunk)
                            downloaded += len(chunk)
                            
                            if progress_callback and total_size > 0:
                                progress = (downloaded / total_size) * 100
                                await progress_callback(url, progress, downloaded, total_size)
                
                logger.info(f"Completed download: {filepath}")
                return True
                
            except Exception as e:
                logger.error(f"Error downloading {url}: {e}")
                return False