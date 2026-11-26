from rest_framework import serializers

from documents.models import DocumentType

FILE_HELP = "A PDF, JPEG or PNG file, up to 10 MB."


class PublishDocumentDto(serializers.Serializer):
    unit_id = serializers.IntegerField()
    document_type = serializers.ChoiceField(choices=DocumentType.values)
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    document_date = serializers.DateField(required=False, allow_null=True)
    tenancy_id = serializers.IntegerField(required=False, allow_null=True)
    maintenance_issue_id = serializers.IntegerField(required=False, allow_null=True)
    file = serializers.FileField(help_text=FILE_HELP)


class AddVersionDto(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    document_date = serializers.DateField(required=False, allow_null=True)
    file = serializers.FileField(help_text=FILE_HELP)


class DocumentListQueryDto(serializers.Serializer):
    unit_id = serializers.IntegerField()


class ConfirmVersionDto(serializers.Serializer):
    idempotency_key = serializers.UUIDField(
        help_text="A fresh id per click. Sending the same one again changes nothing."
    )


class FlagVersionDto(ConfirmVersionDto):
    reason = serializers.CharField(help_text="What is wrong with it.")
