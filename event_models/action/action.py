import datetime
import enum
from collections import defaultdict
from decimal import Decimal
from typing import Annotated, Any, DefaultDict, Optional

from pydantic import BaseModel, Field, model_validator

from event_models.exchange.exchange import EventExchange

type PriceMarkup = DefaultDict[  # type: ignore[valid-type]
    EventExchange,
    Annotated[Decimal, Field(default_factory=Decimal)],
]


class SplitType(enum.Enum):
    CUSTOM = "CUSTOM"
    ANY = "ANY"


# Same as ListingStatus in arb
class ActionStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"
    UPDATED = "UPDATED"
    BLACKLISTED = "BLACKLISTED"
    PARTIALLY_SOLD = "PARTIALLY_SOLD"
    SOLD = "SOLD"
    FINISHED = "FINISHED"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"
    DISABLED_SALE = "DISABLED_SALE"


class ActionError(enum.StrEnum):
    MISSING_MAPPING = "MISSING_MAPPING"
    API_ERROR = "API_ERROR"
    PROCESS_ERROR = "PROCESS_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ActionData(BaseModel):
    source_id: str = Field(description="Source identifier")
    local_datetime: datetime.datetime = Field(description="Local date and time of the event")
    listing_id: int = Field(description="Listing identifier")
    inventory_id: int = Field(description="Inventory identifier")
    section: str = Field(description="Seating section")
    row: str = Field(description="Seating row")
    seats: list[str] = Field(description="List of seat numbers")
    internal_notes: str = Field(description="Internal notes")
    ticket_description: Optional[str] = Field(default=None, description="Ticket description")
    public_notes: str = Field(description="Public notes")
    quantity: int = Field(description="Quantity of tickets")
    tags: list[str] = Field(description="List of tags")
    listing_price: Decimal = Field(description="Listing price")
    original_price: Decimal = Field(description="Original price")
    split_type: SplitType = Field(description="Split type")
    price_markup: PriceMarkup = Field(
        default_factory=defaultdict,
        description="Per-exchange price markup",
    )


class ActionSchema(BaseModel):
    action_id: int
    created: datetime.datetime
    origin_id: int
    new_id: int | None = None
    external_id: int | None = None
    action: ActionStatus
    data: ActionData | None = None
    action_exchange_id: str | None = None
    # TODO check Arb listing structure
    exchange_rules: list[str] | None = None
    external_mapping: dict[EventExchange, int] = {}


class ActionLogSchema(BaseModel):
    action_id: int
    action_exchange_id: str
    action_exchange: EventExchange
    sync_time: datetime.datetime | None = None
    synced: bool
    retryable: bool = Field(default=True)
    error: dict[datetime.datetime, str] | None = None
    error_code: ActionError | None = None

    @model_validator(mode="before")
    def check_error(cls: Any, values: Any) -> Any:
        synced = values.get("synced")

        if synced is True:
            if not values.get("sync_time"):
                raise ValueError("Sync time is required when sync is set to True")

        else:
            if values.get("sync_time"):
                raise ValueError("Sync time is cant be set when sync is set to False")

        return values
