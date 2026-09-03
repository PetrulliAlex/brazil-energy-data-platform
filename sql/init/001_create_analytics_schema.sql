CREATE SCHEMA IF NOT EXISTS analytics;


CREATE TABLE IF NOT EXISTS analytics.monthly_state_production (
    production_date DATE NOT NULL,
    state TEXT NOT NULL,
    production_m3 DOUBLE PRECISION NOT NULL,

    PRIMARY KEY (
        production_date,
        state
    )
);


CREATE TABLE IF NOT EXISTS analytics.monthly_location_production (
    production_date DATE NOT NULL,
    location TEXT NOT NULL,
    production_m3 DOUBLE PRECISION NOT NULL,

    PRIMARY KEY (
        production_date,
        location
    )
);


CREATE TABLE IF NOT EXISTS analytics.yearly_state_production (
    year SMALLINT NOT NULL,
    state TEXT NOT NULL,
    production_m3 DOUBLE PRECISION NOT NULL,
    previous_year_production_m3 DOUBLE PRECISION,
    yoy_growth_pct DOUBLE PRECISION,

    PRIMARY KEY (
        year,
        state
    )
);