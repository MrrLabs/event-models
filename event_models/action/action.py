import datetime
import enum
from collections import defaultdict
from decimal import Decimal
from typing import Annotated, Any, DefaultDict, Literal, Optional, Self

from pydantic import BaseModel, Field, field_validator, model_validator

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
    DEPENDENT_ERROR = "DEPENDENT_ERROR"


class RuleType(enum.StrEnum):
    INCLUDE = "include"
    EXCLUDE = "exclude"


class ExchangeRule(BaseModel):
    exchange: EventExchange
    rule_type: RuleType
    rule_ids: list[int]


class ActionFilterReason(enum.StrEnum):
    EXCHANGE_RULE = "exchange_rule"
    DATE_FILTER = "date_filter"
    MAX_LISTINGS_LIMIT = "max_listings_limit"


class ExchangeSyncConfigSchema(BaseModel):
    exchange: EventExchange
    listings_from: datetime.datetime
    listings_to: datetime.datetime
    listings_limit: int | None
    price_markup: Decimal

    @field_validator("price_markup", mode="before")
    @classmethod
    def validate_price_markup(cls, v: Decimal) -> Decimal:
        return Decimal(v).quantize(Decimal("0.01"))

    @classmethod
    def from_orm(cls, obj: Any) -> Self:
        return cls(
            exchange=EventExchange(obj.exchange),
            listings_from=obj.listings_from,
            listings_to=obj.listings_to,
            listings_limit=obj.listings_limit,
            price_markup=Decimal(obj.price_markup),
        )

    class Config:
        from_attributes = True


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
    split_value: list[int] = Field(description="Custom split configuration")
    price_markup: PriceMarkup = Field(
        default_factory=defaultdict,
        description="Per-exchange price markup",
    )

    @field_validator("split_value", mode="before")
    def validate_split_value(cls, v: str | list[int]) -> list[int]:
        if isinstance(v, str):
            if v.strip() == "":
                return []

            return [int(c) for c in v.split(",") if c.strip()]

        return v


class ActionSchema(BaseModel):
    action_id: int
    action_exchange_id: int | None = None
    action: Literal[ActionStatus.ACTIVE, ActionStatus.UPDATED, ActionStatus.REMOVED] = Field(
        description="Action status", examples=[ActionStatus.ACTIVE, ActionStatus.UPDATED, ActionStatus.REMOVED]
    )
    created: datetime.datetime
    origin_id: int
    exchange: EventExchange | None = None
    new_id: int | None = None
    external_id: int | None = None
    inventory_id: int | None = None
    dependent_to: int | None = None
    post_dependency: int | None = None
    data: ActionData | None = None
    exchange_rules: dict[EventExchange, RuleType] | None = None
    external_mapping: dict[EventExchange, int] | None = {}
    exchange_config: dict[EventExchange, ExchangeSyncConfigSchema] | None = Field(
        default_factory=dict,
        description="Per-exchange sync configuration",
    )
    exchange_count: dict[EventExchange, int] = Field(
        default_factory=dict,
        description="Per-exchange counts",
    )


class ActionLogSchema(BaseModel):
    action_id: int
    action_exchange_id: int | None = None
    action_exchange: EventExchange
    sync_time: datetime.datetime | None = None
    sync_started: datetime.datetime | None = None
    synced: bool
    retryable: bool = Field(default=True)
    error: dict[datetime.datetime, str] | None = None
    error_code: ActionError | None = None
    filter: list[ActionFilterReason] | None = None
    dependent_on: int | None = None
    dependent_to: int | None = None
    notes: str | None = None

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


class ActionErrorRequestSchema(BaseModel):
    action_id: int = Field(description="Action ID")
    error: str = Field(description="Error message")
    error_code: ActionError = Field(description="Error code")
