from properties.dtos.unit_fields import UnitFieldsDto


class UpdateUnitDto(UnitFieldsDto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, partial=True, **kwargs)
