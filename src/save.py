import s3datasource
import paths


def save_classification_rules():
    context = s3datasource.get_context()
    rules_path = paths.get_classification_rules_file_path(context)
    key = context.get_var("RULES_PATH")
    s3datasource.save_object_from_file_path(context, rules_path, key)
