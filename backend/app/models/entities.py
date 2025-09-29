from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from ..db.base import Base


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String(50), primary_key=True)
    market = Column(String(100), nullable=False)
    site_type = Column(String(50))
    start_date = Column(Date)
    end_date_planned = Column(Date)
    end_date_actual = Column(Date)

    milestones = relationship("Milestone", back_populates="project", cascade="all,delete")


class Agent(Base):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True)
    agent_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    milestones = relationship("Milestone", back_populates="agent")


class Milestone(Base):
    __tablename__ = "milestones"

    milestone_id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"))
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    milestone_name = Column(String(150), nullable=False)
    planned_date = Column(Date)
    actual_date = Column(Date)
    status = Column(String(30))
    duration_days = Column(Integer)
    anomaly_flag = Column(Boolean, default=False)

    project = relationship("Project", back_populates="milestones")
    agent = relationship("Agent", back_populates="milestones")
    dependencies = relationship("Dependency", foreign_keys="Dependency.milestone_id", cascade="all,delete")
    prerequisites = relationship("Dependency", foreign_keys="Dependency.prerequisite_id")
    anomalies = relationship("Anomaly", cascade="all,delete")
    milestone_vendors = relationship("MilestoneVendor", cascade="all,delete")


class Dependency(Base):
    __tablename__ = "dependencies"

    dependency_id = Column(Integer, primary_key=True)
    milestone_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"))
    prerequisite_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"))
    dependency_type = Column(String(30))


class Vendor(Base):
    __tablename__ = "vendors"

    vendor_id = Column(Integer, primary_key=True)
    vendor_name = Column(String(150), unique=True, nullable=False)
    role = Column(String(100))

    milestone_links = relationship("MilestoneVendor", cascade="all,delete")


class MilestoneVendor(Base):
    __tablename__ = "milestone_vendors"

    milestone_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"), primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.vendor_id", ondelete="CASCADE"), primary_key=True)
    contribution = Column(String(255))


class Anomaly(Base):
    __tablename__ = "anomalies"

    anomaly_id = Column(Integer, primary_key=True)
    milestone_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"))
    type = Column(String(100))
    description = Column(Text)
    severity = Column(String(20))
    detected_on = Column(TIMESTAMP)


class CycleTime(Base):
    __tablename__ = "cycle_times"

    cycle_id = Column(Integer, primary_key=True)
    project_id = Column(String(50), ForeignKey("projects.project_id", ondelete="CASCADE"))
    agent_start_id = Column(Integer, ForeignKey("agents.agent_id"))
    agent_end_id = Column(Integer, ForeignKey("agents.agent_id"))
    planned_duration = Column(Integer)
    actual_duration = Column(Integer)
    variance = Column(Integer)
