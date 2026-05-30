WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

carts AS (
    SELECT * FROM {{ ref('stg_carts') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
),

users AS (
    SELECT * FROM {{ ref('stg_users') }}
),

tag_enriched AS (
    SELECT * FROM {{ source('post_ingest_ecommerce', 'stg_product_tag_enriched') }}
),

enriched AS (
    SELECT
        -- Identifiers
        o.cart_id,
        o.customer_id,
        o.product_id,

        -- Customer details
        u.first_name,
        u.last_name,
        u.email,
        u.age,
        u.gender,
        u.city,
        u.state,
        u.country,
        u.company_name,
        u.company_department,

        -- Product details
        p.product_name,
        p.product_category,
        t.product_tag,
        p.brand,
        p.availability_status,
        p.rating,
        p.stock_quantity,
        p.weight,
        p.return_policy,
        p.shipping_information,
        p.warranty_information,
        p.thumbnail_url,

        -- Order item metrics
        o.unit_price,
        o.quantity,
        o.item_total,
        o.item_discount_pct,
        o.item_discounted_total,
        o.item_total - o.item_discounted_total AS discount_savings,
        o.item_thumbnail_url,

        -- Cart level metrics
        c.cart_total,
        c.cart_discounted_total,
        c.total_products,
        c.total_quantity,

        -- Metadata
        o.ingested_at

    FROM orders o
    LEFT JOIN carts c ON o.cart_id = c.cart_id
    LEFT JOIN products p ON o.product_id = p.product_id
    LEFT JOIN users u ON o.customer_id = u.customer_id
    LEFT JOIN tag_enriched t ON o.product_id = t.product_id
)

SELECT * FROM enriched