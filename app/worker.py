"""
Example background worker process
This demonstrates running a background task alongside the main application
"""

import time
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('worker')

def main():
    """
    Example worker that runs continuously
    Replace this with your actual background job logic
    """
    logger.info("Worker process starting...")
    logger.info(f"Environment: {os.getenv('APP_ENV', 'development')}")

    iteration = 0

    while True:
        try:
            iteration += 1
            logger.info(f"Worker iteration {iteration} - Processing tasks...")

            # Simulate some work
            # Replace this with your actual background job logic:
            # - Process queue messages
            # - Run scheduled tasks
            # - Clean up old data
            # - Send notifications
            # etc.

            time.sleep(30)  # Sleep for 30 seconds between iterations

            if iteration % 10 == 0:
                logger.info(f"Worker health check - {iteration} iterations completed")

        except KeyboardInterrupt:
            logger.info("Worker received shutdown signal")
            break
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            # Sleep before retrying
            time.sleep(5)

    logger.info("Worker process shutting down...")

if __name__ == '__main__':
    main()
