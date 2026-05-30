WITH orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
),

final AS (
    SELECT
        -- Identifiers
        cart_id,
        customer_id,
        product_id,

        -- Customer details
        first_name,
        last_name,
        email,
        gender,
        age,
        CASE
            WHEN age BETWEEN 18 AND 25 THEN '18-25'
            WHEN age BETWEEN 26 AND 35 THEN '26-35'
            WHEN age BETWEEN 36 AND 45 THEN '36-45'
            WHEN age BETWEEN 46 AND 55 THEN '46-55'
            ELSE '55+'
        END                                     AS age_group,

        -- Location
        city,
        state,
        country,

        -- Company
        company_name,
        company_department,

        -- Product details
        product_name,
        product_category,
        product_tag,
        brand,
        availability_status,
        rating,
        stock_quantity,
        weight,
        return_policy,
        shipping_information,
        warranty_information,
        thumbnail_url,

        -- Sales metrics
        unit_price,
        quantity,
        item_total                              AS gross_revenue,
        item_discounted_total                   AS net_revenue,
        discount_savings,
        item_discount_pct                       AS discount_pct,

        -- Cart level metrics
        cart_total                              AS gross_cart_total,
        cart_discounted_total                   AS net_cart_total,
        total_products,
        total_quantity,

        -- Metadata
        ingested_at

    FROM orders
)

SELECT * FROM final