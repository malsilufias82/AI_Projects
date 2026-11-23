from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from app.models.mongo_base import MongoBaseModel, TimestampMixin


class Week0Column(BaseModel):
	name: str
	label: str
	field: str
	align: str = "left"
	classes: Optional[str] = None
	headerClasses: Optional[str] = None


class Week0Row(BaseModel):
	id: int
	activity: str = ""
	relevantLink: str = ""
	technology: str = "Applicable for all"
	project: str = "Applicable for all projects"
	comment: str = ""
	blocker: str = ""
	status: Literal["Pending", "Completed"] = "Pending"


class Week0Tracker(MongoBaseModel, TimestampMixin):
	"""MongoDB document for Week 0 tracker table metadata and rows."""

	key: str = Field(default="default", max_length=100)
	columns: List[Week0Column] = Field(default_factory=list)
	rows: List[Week0Row] = Field(default_factory=list)
	updated_by: Optional[str] = Field(default=None, max_length=255)

	class Config:
		collection_name = "mongo_week0"
