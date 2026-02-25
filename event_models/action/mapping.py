import datetime

from pydantic import BaseModel, Field, PositiveInt

from event_models.exchange.exchange import EventExchange


class ListingExchangeBaseMappingSchema(BaseModel):
    action_id: PositiveInt = Field(gt=0, examples=[1])
    listing_id: PositiveInt = Field(gt=0, examples=[1])
    exchange: EventExchange
    full_sync: bool = Field(default=False)


class ListingExchangeMappingRequestSchema(ListingExchangeBaseMappingSchema):
    inventory_id: PositiveInt = Field(gt=0, examples=[1])
    external_id: PositiveInt = Field(gt=0, examples=[1])
    valid_from: datetime.datetime = Field(examples=["2023-10-01T12:00:00"])


class UpdateListingMappingRequestSchema(ListingExchangeBaseMappingSchema):
    inventory_id: PositiveInt = Field(gt=0, examples=[1])
    valid_to: datetime.datetime = Field(examples=["2023-10-01T12:00:00"])
