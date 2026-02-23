from enum import StrEnum


# TODO unify with EventSource from event_models.event.event
class ScrapType(StrEnum):
    TICKETMASTER_MAP = "ticketmaster-map"
    TICKETMASTER_FACET = "ticketmaster-facet"
    VIVIDSEATS = "vividseats"
    EVENUE_SEAT = "evenue-seat"
    EVENUE_SECTION = "evenue-section"
    EVENUE_PRICES = "evenue-prices"
    STUBHUB = "stubhub"
    TICKPICK = "tickpick"
    GOTICKETS = "gotickets"
    MILB = "milb"
    MLB = "mlb"
    GAMETIME = "gametime"
    PLAYHOUSESQUARE = "playhousesquare"
    TELECHARGE = "telecharge"
    MPV = "mpv"
    ETIX = "etix"
    EVENTIM = "eventim"


class FailureReason(StrEnum):
    ACCESS_DENIED = "access_denied"
    PROXY_ERROR = "proxy_error"
    NOT_FOUND = "not_found"
    SCRAP_SERVICE_OVERLOAD = "scrap_service_overload"
    DATA_ISSUE = "data_issue"
    PROCESS_SERVICE_OVERLOAD = "process_service_overload"
    NO_SECTIONS = "no_sections"
    NOT_ON_SALE = "not_on_sale"
    SOLD_OUT = "sold_out"
    DATA_PROCESS_ERROR = "data_process_error"
    SEATS_FOUND_WITH_NO_MAP = "seats_found_with_no_map"
    DATA_STORAGE_ERROR = "data_storage_error"
    DUPLICATE_PLACE_ID = "duplicate_place_id"
    TIMEOUT = "timeout"
    TRIGGER_PROCESS_ERROR = "trigger_process_error"
    DEFAULT = "default"
