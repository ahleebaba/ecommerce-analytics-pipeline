{# individual products extracted from the cart ingestion table #}

WITH source AS (
    SELECT * FROM {{ source('ingest_ecommerce', 'carts') }}
),

unnested AS (
    SELECT
        -- Cart level fields
        id                                              AS cart_id,
        userId                                          AS customer_id,

        -- Product level fields (unnested from JSON array)
        CAST(JSON_VALUE(item, '$.id') AS INT64)         AS product_id,
        JSON_VALUE(item, '$.title')                     AS product_name,
        CAST(JSON_VALUE(item, '$.price') AS FLOAT64)    AS unit_price,
        CAST(JSON_VALUE(item, '$.quantity') AS INT64)   AS quantity,
        CAST(JSON_VALUE(item, '$.total') AS FLOAT64)    AS item_total,
        CAST(JSON_VALUE(item, '$.discountPercentage') AS FLOAT64) AS item_discount_pct,
        CAST(JSON_VALUE(item, '$.discountedTotal') AS FLOAT64)    AS item_discounted_total,
        JSON_VALUE(item, '$.thumbnail') AS item_thumbnail_url,

         -- Cart level fields
        -- Airbyte metadata
        _airbyte_extracted_at                           AS ingested_at

    FROM source,
    UNNEST(JSON_QUERY_ARRAY(products)) AS item
)

SELECT * FROM unnested