import datetime
from typing import Any

from pydantic import BaseModel, PositiveInt, Field

from event_models.exchange.exchange import EventExchange


class ListingExchangeBaseMappingSchema(BaseModel):
    action_id: PositiveInt = Field(gt=0, examples=[1])
    listing_id: PositiveInt = Field(gt=0, examples=[1])
    exchange: EventExchange
    full_sync: bool = Field(default=False)


class ListingExchangeMappingRequestSchema(ListingExchangeBaseMappingSchema):
    action_exchange_id_create: PositiveInt | None = Field(gt=0, examples=[1])
    inventory_id: PositiveInt = Field(gt=0, examples=[1])
    external_id: PositiveInt = Field(gt=0, examples=[1])
    valid_from: datetime.datetime = Field(examples=["2023-10-01T12:00:00"])

    def to_db_store(self) -> dict[str, Any]:
        return {
            "inventory_id": self.inventory_id,
            "source_listing_id": self.listing_id,
            "exchange": self.exchange.value,
            "external_id": self.external_id,
            "valid_from": self.valid_from,
            "full_sync": self.full_sync,
            "action_exchange_id_create": self.action_exchange_id_create,
        }


class UpdateListingMappingRequestSchema(ListingExchangeBaseMappingSchema):
    inventory_id: PositiveInt = Field(gt=0, examples=[1])
    valid_to: datetime.datetime = Field(examples=["2023-10-01T12:00:00"])
    action_exchange_id_update: PositiveInt | None = Field(gt=0, examples=[1])
