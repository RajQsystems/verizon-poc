from abc import ABC, abstractmethod
from typing import List, Dict, Any
import pandas as pd


class AlertInterface(ABC):

    @abstractmethod
    async def fetch_projects(self) -> pd.DataFrame:
        """Fetch projects + milestones data from DB."""
        pass

    @abstractmethod
    async def build_report(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Transform raw milestone data into risk report JSON."""
        pass
