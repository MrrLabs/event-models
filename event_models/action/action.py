import datetime
import enum
from collections import defaultdict
from decimal import Decimal
from typing import Annotated, Any, DefaultDict, Optional, Self

from pydantic import BaseModel, Field, field_validator

from event_models.exchange.exchange import EventExchange

type PriceMarkup = DefaultDict[  # type: ignore[valid-type]
    EventExchange,
    Annotated[Decimal, Field(default_factory=Decimal)],
]


class SplitType(enum.Enum):
    CUSTOM = "CUSTOM"
    ANY = "ANY"


class StockType(enum.Enum):
    ELECTRONIC = "ELECTRONIC"
    MOBILE_SCREENCAP = "MOBILE_SCREENCAP"
    MOBILE_TRANSFER = "MOBILE_TRANSFER"


# Same as ListingStatus in arb
class ActionStatus(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SYNC = "SYNC"
    SYNC_CREATE = "SYNC_CREATE"
    SYNC_UPDATE = "SYNC_UPDATE"
    SYNC_DELETE = "SYNC_DELETE"


class ActionError(enum.StrEnum):
    MISSING_MAPPING = "MISSING_MAPPING"
    MISSING_EVENT_MAPPING = "MISSING_EVENT_MAPPING"
    INVALID_EVENT_MAPPING = "INVALID_EVENT_MAPPING"
    API_ERROR = "API_ERROR"
    PROCESS_ERROR = "PROCESS_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    DEPENDENT_ERROR = "DEPENDENT_ERROR"
    LISTING_EXISTS = "LISTING_EXISTS_ERROR"
    SEND_TO_MAPPING = "SEND_TO_MAPPING"
    UNAVAILABLE_FOR_LISTING = "UNAVAILABLE_FOR_LISTING"
    UPDATE_FORBIDDEN_ERROR = "UPDATE_FORBIDDEN"
    EVENT_MERGED = "EVENT_MERGED"
    PRICE_EXCEEDS = "PRICE_EXCEEDS"
    INVALID_SECTION = "INVALID_SECTION"


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
    event_name: str = Field(description="Event name")
    venue_name: str = Field(description="Venue name")
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
    stock_type: StockType = Field(description="Stock type")
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
