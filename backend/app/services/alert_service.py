import pandas as pd
import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from backend.app.services.interface.alert_interface import AlertInterface


class AlertService(AlertInterface):
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def safe_days(
        end: Optional[pd.Timestamp], start: Optional[pd.Timestamp]
    ) -> Optional[int]:
        # Handles None/NaN/NaT gracefully
        if pd.isna(end) or pd.isna(start):
            return None
        return int((end - start).days)

    async def fetch_projects(self) -> pd.DataFrame:
        query = text(
            """
            SELECT 
                fuze_project_id,
                site_name,
                local_market,
                county,
                site_candidate_type,
                structure_owner,
                vendor_site_acquisition,
                vendor_construction_manager_company,
                transport_vendor,
                project_status,
                project_started_milestone_a AS project_start,
                real_estate_completed_rec_milestone_a AS rec,
                equip_received_a AS rer,
                ready_to_construct_rtc_milestone_a AS rtc,
                physical_construction_completed_a AS pcc,
                transport_awarded_a,
                transport_completed_a,
                building_permit_approved_a,
                nepa_complete_a
            FROM public.projects_encoded
            """
        )

        result = await self.db.execute(query)
        rows = result.fetchall()
        columns = result.keys()

        df = pd.DataFrame(rows, columns=columns)

        # Convert date-like columns into datetime
        date_cols = [
            "project_start",
            "rec",
            "rer",
            "rtc",
            "pcc",
            "transport_awarded_a",
            "transport_completed_a",
            "building_permit_approved_a",
            "nepa_complete_a",
        ]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Replace NaN and NaT with None to ensure JSON-compliant values downstream
        df = df.replace({np.nan: None})

        return df

    def build_report(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        projects_json: List[Dict[str, Any]] = []

        for _, row in df.iterrows():
            durations = {
                "start_to_rer": self.safe_days(
                    row.get("rer"), row.get("project_start")
                ),
                "rec_to_rer": self.safe_days(row.get("rer"), row.get("rec")),
                "rec_to_rtc": self.safe_days(row.get("rtc"), row.get("rec")),
                "rtc_to_pcc": self.safe_days(row.get("pcc"), row.get("rtc")),
                "transport_awarded_to_completed": self.safe_days(
                    row.get("transport_completed_a"), row.get("transport_awarded_a")
                ),
            }

            risk_flags: List[str] = []
            if row.get("building_permit_approved_a") is None:
                risk_flags.append("Missing Building Permit Approval")
            if row.get("nepa_complete_a") is None:
                risk_flags.append("NEPA Compliance Missing")
            if (
                durations["start_to_rer"] is not None
                and durations["start_to_rer"] > 365
            ):
                risk_flags.append("Duration exceeds threshold for market")

            def fmt_date(val):
                if isinstance(val, pd.Timestamp) and not pd.isna(val):
                    return val.strftime("%Y-%m-%d")
                return None

            project_data: Dict[str, Any] = {
                "fuze_project_id": row.get("fuze_project_id"),
                "site_name": row.get("site_name"),
                "local_market": row.get("local_market"),
                "county": row.get("county"),
                "site_candidate_type": row.get("site_candidate_type"),
                "structure_owner": row.get("structure_owner"),
                "vendor_site_acquisition": row.get("vendor_site_acquisition"),
                "vendor_construction_manager_company": row.get(
                    "vendor_construction_manager_company"
                ),
                "transport_vendor": row.get("transport_vendor"),
                "project_status": row.get("project_status"),
                "dates": {
                    "project_start": fmt_date(row.get("project_start")),
                    "rec": fmt_date(row.get("rec")),
                    "rer": fmt_date(row.get("rer")),
                    "rtc": fmt_date(row.get("rtc")),
                    "pcc": fmt_date(row.get("pcc")),
                },
                "durations": durations,
                "risk_flags": risk_flags,
                "aggregates": {},
            }

            projects_json.append(project_data)

        # Vendor-level aggregate: median of start_to_rer, cast to int or None
        def median_safe(series: pd.Series) -> Optional[int]:
            med = series.median()
            if pd.isna(med):
                return None
            try:
                return int(med)
            except Exception:
                return None

        # Recompute per group using safe_days to ensure JSON-safe values
        vendor_agg = (
            df.groupby("vendor_site_acquisition", dropna=False)
            .apply(
                lambda g: {
                    "median_start_to_rer": median_safe(
                        g.apply(
                            lambda x: self.safe_days(
                                x.get("rer"), x.get("project_start")
                            ),
                            axis=1,
                        )
                    )
                }
            )
            .to_dict()
        )

        for p in projects_json:
            vendor = p.get("vendor_site_acquisition")
            if vendor in vendor_agg:
                p["aggregates"]["vendor"] = vendor_agg[vendor]

        return projects_json

    async def get_full_report(self) -> List[Dict[str, Any]]:
        df = await self.fetch_projects()
        return self.build_report(df)
