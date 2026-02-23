import datetime
import enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


# TODO unify with ScrapType from trigger.enum
class EventSource(enum.StrEnum):
    TICKETMASTER_MAP = "ticketmaster-map"
    TICKETMASTER_FACET = "ticketmaster-facet"
    VIVIDSEATS = "vividseats"
    EVENUE_SEAT = "evenue-seat"
    STUBHUB = "stubhub"
    TICKPICK = "tickpick"
    GOTICKETS = "gotickets"
    MILB = "milb"
    MLB = "mlb"
    PLAYHOUSESQUARE = "playhousesquare"
    TELECHARGE = "telecharge"
    MPV = "mpv"
    ETIX = "etix"
    EVENTIM = "eventim"


class EventStoreType(enum.StrEnum):
    TICKETMASTER = "ticketmaster"
    VIVIDSEATS = "vividseats"
    EVENUE = "evenue"
    TICKPICK = "tickpick"
    STUBHUB = "stubhub"
    GOTICKETS = "gotickets"
    MILB = "milb"
    MLB = "mlb"
    PLAYHOUSESQUARE = "playhousesquare"
    TELECHARGE = "telecharge"
    MPV = "mpv"
    ETIX = "etix"
    EVENTIM = "eventim"


class EventAction(enum.StrEnum):
    # store data
    STORE = "store"
    NOTIFY = "notify"
    # archive event or venue - there won't be any more data for this event/venue
    ARCHIVE = "archive"
    # store with full update of the data, all columns are compared and possibly updated
    FULL_UPDATE = "full-update"


class MessageHeader(BaseModel):
    event_message_id: str = Field(alias="event-message-id")
    event_source: EventSource = Field(alias="event-source")
    # set by each child class
    venue_id: str | None = Field(alias="venue-id", default=None)
    event_id: str = Field(alias="event-id")
    event_action: EventAction = Field(default=EventAction.STORE, alias="event-action")
    event_timestamp: datetime.datetime | None = Field(alias="event-timestamp", default=None)
    no_map: bool | None = Field(default=False, alias="no-map")
    not_found: bool | None = Field(default=False, alias="not-found")
    not_on_sale: bool | None = Field(default=False, alias="not-on-sale")

    model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)

    @field_validator("event_timestamp", mode="after")
    def set_default_timezone(cls: Any, v: datetime.datetime) -> datetime.datetime:
        # check if v has timezone info
        if v and v.tzinfo:
            return v
        # else return current v and set timezone to UTC
        else:
            return v.replace(tzinfo=datetime.timezone.utc)

    def to_archive(self) -> "ArchiveMessage":
        return ArchiveMessage(
            message_id=self.event_message_id,
            venue_id=self.venue_id,
            event_id=self.event_id,
            event_timestamp=self.event_timestamp,
        )


class EventMessage(BaseModel):
    header: MessageHeader


class ArchiveMessage(BaseModel):
    message_id: str
    venue_id: str
    event_id: str = Field(default="")
    event_timestamp: datetime.datetime
