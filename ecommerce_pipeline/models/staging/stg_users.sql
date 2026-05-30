WITH source AS (
    SELECT * FROM {{ source('ingest_ecommerce', 'users') }}
),

renamed AS (
    SELECT
        -- Primary key
        id                                              AS customer_id,

        -- Name
        firstName                                       AS first_name,
        lastName                                        AS last_name,

        -- Contact
        email                                           AS email,
        phone                                           AS phone,

        -- Demographics
        age                                             AS age,
        gender                                          AS gender,
        birthDate                                       AS birth_date,

        -- Home address (nested JSON)
        JSON_VALUE(address, '$.city')                   AS city,
        JSON_VALUE(address, '$.state')                  AS state,
        JSON_VALUE(address, '$.country')                AS country,
        JSON_VALUE(address, '$.postalCode')             AS postal_code,

        -- Company
        JSON_VALUE(company, '$.name')                   AS company_name,
        JSON_VALUE(company, '$.department')             AS company_department,
        JSON_VALUE(company, '$.address.city')           AS company_city,

        -- Airbyte metadata
        _airbyte_extracted_at                           AS ingested_at

    FROM source
)

SELECT * FROM renamed