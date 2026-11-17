from providers.dtos.provider_fields import ProviderFieldsDto


class UpdateProviderDto(ProviderFieldsDto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, partial=True, **kwargs)
