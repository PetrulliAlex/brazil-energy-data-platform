# Brazil Energy Data Platform

Production-style data engineering project that ingests, processes and serves
Brazilian energy and economic data.

## Business Problem

Energy analysts often need to combine data from multiple public sources with
different formats, schemas and update frequencies.

This project builds an automated data platform that ingests public Brazilian
energy and macroeconomic datasets and transforms them into reliable,
analytics-ready data products.

## Architecture

Sources → Raw Storage → Bronze → Silver → Gold → PostgreSQL → API / Analytics

## Engineering Goals

- Automated ingestion
- Incremental processing
- Idempotent pipelines
- Data quality validation
- Orchestration with Airflow
- Distributed transformations with Spark
- Reproducible local environment using Docker
- Automated testing and CI
- Analytics-ready dimensional models

## Tech Stack

Python | SQL | Apache Spark | Airflow | PostgreSQL | Docker | MinIO | FastAPI | GitHub Actions