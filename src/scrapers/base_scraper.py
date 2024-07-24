from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

class BaseScraper(ABC):
    def __init__(self, date_range: tuple, job_categories: List[str], location: str):
        self.date_range = self._parse_date_range(date_range)
        self.job_categories = self._validate_job_categories(job_categories)
        self.location = location
        self.logger = logging.getLogger(self.__class__.__name__)

    def _parse_date_range(self, date_range: tuple) -> tuple:
        start_date, end_date = date_range
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_date > end_date:
            raise ValueError("Start date must be before end date")
        
        return start_date, end_date

    def _validate_job_categories(self, job_categories: List[str]) -> List[str]:
        valid_categories = [
            "Software Development",
            "Data Science and Analytics",
            "Cloud Computing and DevOps",
            "Cybersecurity",
            "Artificial Intelligence and Machine Learning"
        ]
        invalid_categories = set(job_categories) - set(valid_categories)
        if invalid_categories:
            raise ValueError(f"Invalid job categories: {', '.join(invalid_categories)}")
        return job_categories

    @abstractmethod
    def generate_search_url(self) -> str:
        """Generate the initial search URL based on input parameters."""
        pass

    @abstractmethod
    def scrape_job_listings(self) -> List[Dict[str, Any]]:
        """Scrape job listings based on the search parameters."""
        pass

    @abstractmethod
    def extract_job_details(self, job_url: str) -> Dict[str, Any]:
        """Extract detailed information from a specific job posting."""
        pass

    @abstractmethod
    def handle_pagination(self, current_page: int) -> str:
        """Handle pagination and return the URL for the next page."""
        pass

    @abstractmethod
    def map_job_category(self, category: str) -> str:
        """Map general job category to site-specific category."""
        pass

    def run_scraper(self) -> List[Dict[str, Any]]:
        """Main method to run the scraping process."""
        self.logger.info(f"Starting scraping process for {self.__class__.__name__}")
        all_jobs = []
        search_url = self.generate_search_url()
        current_page = 1

        while search_url:
            self.logger.info(f"Scraping page {current_page}")
            job_listings = self.scrape_job_listings()
            for job in job_listings:
                job_details = self.extract_job_details(job['url'])
                all_jobs.append(job_details)
            
            search_url = self.handle_pagination(current_page)
            current_page += 1

        self.logger.info(f"Scraping complete. Total jobs scraped: {len(all_jobs)}")
        return all_jobs

    def get_date_range_params(self) -> Dict[str, str]:
        """Convert date range to a format suitable for URL parameters."""
        start_date, end_date = self.date_range
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }