try:
    import great_expectations as gx
except Exception:
    gx = None


def validate(df):
    if gx is None:
        return True
    context = gx.get_context()
    batch = context.get_validator(df)
    batch.expect_column_values_to_not_be_null("Close")
    return batch.validate().success
