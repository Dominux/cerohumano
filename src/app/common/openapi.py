from fastapi.openapi.utils import get_openapi

# --- SWAGGER ARRAY<STRING> FILE PICKER PATCH ---
def custom_openapi(app):
    def wrapper():
        if app.openapi_schema:
            return app.openapi_schema

        # 1. Generate the standard schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        # 2. Walk through schemas and inject the missing "binary" format for lists of files
        components = openapi_schema.get("components", {})
        schemas = components.get("schemas", {})

        for schema_name, schema in schemas.items():
            properties = schema.get("properties", {})
            for prop_name, prop_val in properties.items():
                # If it's an array of strings meant to be octet-streams, force binary format
                if prop_val.get("type") == "array" and "items" in prop_val:
                    items = prop_val["items"]
                    if items.get("type") == "string" and items.get("contentMediaType") == "application/octet-stream":
                        items["format"] = "binary"  # <-- This forces Swagger to show the file picker

        app.openapi_schema = openapi_schema
        return app.openapi_schema
    return wrapper
