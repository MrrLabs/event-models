import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, field_validator

_ORIGINAL_REDIS_SCHEMA_LEN = 7
_ORIGINAL_REDIS_SCHEMA_GA_LEN = 8
_NEW_REDIS_SCHEMA_LEN = 18


class TicketmasterPlaceAvailable(BaseModel):
    # Existing redis schema
    list_price: Decimal
    total_price: Decimal
    offer_id: str | None = None
    offer_name: str
    sellable_quantities: list[int] | None = None
    protected: bool
    inventory_type: str
    # Has value - GA, otherwise None
    count: int | None = None

    # added to fit available/update endpoint
    # place_id: str,
    # TODO temporary to none to be able to work with old schema
    full_section: str | None
    # TODO temporary to none to be able to work with old schema
    section: str | None
    # TODO temporary to none to be able to work with old schema
    row: str | None
    # TODO temporary to none to be able to work with old schema
    row_rank: int | None
    seat_rank: int | None
    # TODO temporary to none to be able to work with old schema
    seat_number: str | None
    attributes: list[str]
    # offer_id: str | None,
    # offer_name: str | None,
    # sellable_quantities: list[int] | None,
    # protected: bool | None,
    description: list[str]
    # inventory_type: str | None,
    # list_price: Decimal | None,
    # total_price: Decimal | None,
    # TODO temporary to none to be able to work with old schema
    inserted: datetime.datetime | None
    prev_updated: datetime.datetime | None
    update_reason: str | None

    @field_validator("list_price", "total_price", mode="before")
    def set_decimal_places(cls, v: Any) -> Decimal:
        if isinstance(v, str):
            return Decimal(f"{float(v):.2f}")

        return Decimal(f"{v:.2f}")


class TicketmasterEventAvailable(BaseModel):
    event_id: str
    places: dict[str, TicketmasterPlaceAvailable]
    old_schema: bool

    @classmethod
    def from_place_dict(
        cls,
        event_id: str,
        input_dict: dict[str, Any],
    ) -> "TicketmasterEventAvailable":
        places: dict[str, TicketmasterPlaceAvailable] = {}
        origin_count = 0
        new_count = 0

        for place_id, value_list in input_dict.items():
            if isinstance(value_list[0], float):
                list_price_float = value_list[0]
            else:
                # string to float conversion -> to be sure the data has a correct format when floating point is used
                list_price_float = float(value_list[0])

            if isinstance(value_list[1], float):
                total_price_float = value_list[1]
            else:
                # string to float conversion -> to be sure the data has a correct format when floating point is used
                total_price_float = float(value_list[1])

            curr_len = len(value_list)

            # old format
            if curr_len in (_ORIGINAL_REDIS_SCHEMA_LEN, _ORIGINAL_REDIS_SCHEMA_GA_LEN):
                origin_count += 1

                places[place_id] = TicketmasterPlaceAvailable(
                    list_price=Decimal(f"{list_price_float:.2f}"),
                    total_price=Decimal(f"{total_price_float:.2f}"),
                    offer_id=str(value_list[2]),
                    offer_name=str(value_list[3]),
                    sellable_quantities=value_list[4],
                    protected=bool(value_list[5]),
                    inventory_type=str(value_list[6]),
                    count=value_list[7] if curr_len == _ORIGINAL_REDIS_SCHEMA_GA_LEN else None,
                    full_section=None,
                    section=None,
                    row=None,
                    row_rank=None,
                    seat_rank=None,
                    seat_number=None,
                    attributes=[],
                    description=[],
                    # during the processing, the avail endpoint needs to be called to get relevant data
                    inserted=None,
                    prev_updated=None,
                    update_reason=None,
                )

            elif len(value_list) == _NEW_REDIS_SCHEMA_LEN:
                new_count += 1

                places[place_id] = TicketmasterPlaceAvailable(
                    #
                    list_price=Decimal(f"{list_price_float:.2f}"),
                    total_price=Decimal(f"{total_price_float:.2f}"),
                    offer_id=str(value_list[2]),
                    offer_name=str(value_list[3]),
                    sellable_quantities=value_list[4],
                    protected=bool(value_list[5]),
                    inventory_type=str(value_list[6]),
                    count=value_list[7],
                    full_section=str(value_list[8]),
                    section=str(value_list[9]),
                    row=str(value_list[10]),
                    row_rank=int(value_list[11]) if value_list[11] is not None else None,
                    seat_rank=int(value_list[12]) if value_list[12] is not None else None,
                    seat_number=str(value_list[13]) if value_list[13] is not None else None,
                    attributes=value_list[14],
                    description=value_list[15],
                    inserted=datetime.datetime.fromisoformat(value_list[16]),
                    prev_updated=datetime.datetime.fromisoformat(str(value_list[17])) if value_list[17] else None,
                    update_reason=value_list[18],
                )
            else:
                raise ValueError(
                    f"Unexpected number of values in redis dict for event {event_id}: {len(value_list)} - {value_list}"
                )

        if origin_count and new_count:
            raise ValueError(
                f"Found {origin_count} old schema values and {new_count} new schema values for event {event_id}"
            )

        return cls(event_id=event_id, places=places, old_schema=origin_count > 0)

    def to_redis_dict(self) -> dict[str, Any]:
        if self.old_schema:
            raise ValueError(f"{self.event_id}: cannot convert to old schema")

        return {
            place_id: [
                str(place_data.list_price),
                str(place_data.total_price),
                place_data.offer_id,
                place_data.offer_name,
                place_data.sellable_quantities,
                place_data.protected,
                place_data.inventory_type,
                place_data.count,
                place_data.full_section,
                place_data.section,
                place_data.row,
                place_data.row_rank,
                place_data.seat_rank,
                place_data.seat_number,
                place_data.attributes,
                place_data.description,
                place_data.inserted.isoformat(),  # type: ignore[union-attr]
                place_data.prev_updated.isoformat() if place_data.prev_updated else None,
                place_data.update_reason if place_data.update_reason else None,
            ]
            for place_id, place_data in self.places.items()
        }

    @classmethod
    def from_event_models(cls, event_id: str, event_data: list[BaseModel]) -> "TicketmasterEventAvailable":
        places: dict[str, TicketmasterPlaceAvailable] = {}

        for place_data in event_data:
            dump_dict = place_data.model_dump()

            if dump_dict.get("protected") is None:
                dump_dict["protected"] = False

            places[dump_dict["place_id"]] = TicketmasterPlaceAvailable(**dump_dict)

        return cls(event_id=event_id, places=places, old_schema=False)
