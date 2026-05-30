WITH source AS (
    SELECT * FROM {{ source('ingest_ecommerce', 'categories') }}
),

renamed AS (
    SELECT
        -- Primary key
        slug                        AS category_slug,

        -- Category details
        name                        AS category_name,
        url                         AS category_url,

        -- Airbyte metadata
        _airbyte_extracted_at       AS ingested_at

    FROM source
)

SELECT * FROM renamed