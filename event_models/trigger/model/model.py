import datetime
from typing import Any, Optional

from pydantic import UUID4, BaseModel, model_validator, NonNegativeInt, Field

from event_models.trigger.enum import FailureReason, ScrapType


class JobRunMessage(BaseModel):
    job_run_id: UUID4
    event_id: str
    scrap_type: ScrapType
    run_config: Optional[dict[str, Any]] | None = None
    retry: NonNegativeInt = Field(default=0)


class JobScrapMessage(BaseModel):
    event_id: str
    job_id: UUID4
    scrap_type: ScrapType | None = None
    job_scrap_started_at: datetime.datetime | None = None
    job_scrap_finished_at: datetime.datetime | None = None
    scrap_success: Optional[bool] = None
    failure_reason: Optional[FailureReason] | None = None
    scrap_notes: Optional[dict[str, Any]] | None = None

    @model_validator(mode="before")
    def check_failure_reason(cls: Any, values: Any) -> Any:
        if values["scrap_success"] is False and values.get("failure_reason") is None:
            raise ValueError("failure_reason must be provided if the job failed.")

        return values
