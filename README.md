# redis-caching-patterns

## What it does

This is a cache-aside project built with FastAPI, PostgreSQL and Redis. The goal is to limit the number of requests that reach the database. When `GET /products/{id}` receives a request, the app first checks Redis for the key `product:{id}`, whose value is a JSON copy of the product. If the key exists, the response comes straight from the cache. If not, the app reads the product from the database, stores it in Redis for 10 minutes, and returns it.

When a product is updated with `PUT /products/{id}`, its cache key is deleted, so the next `GET` reads the new version from the database. Ids that don't exist are also cached for a short time, so repeated requests for them don't reach the database either.

## How to run

Prerequisites: Python 3.13, Docker Desktop, Git.

Ports 5432 and 6379 must be free. If PostgreSQL or Redis is installed locally (for example with Homebrew), stop it first: `brew services stop redis`.

```bash
# 1. Clone
git clone https://github.com/ilyesOuakouak/redis-caching-patterns.git
cd redis-caching-patterns

# 2. Virtual environment, dependencies, settings
python3.13 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 3. Start PostgreSQL and Redis
docker compose up -d

# 4. Create the test database, then the tables in both databases
docker exec cache-pg psql -U app -d cache_demo -c "CREATE DATABASE cache_demo_test;"
alembic upgrade head
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/cache_demo_test alembic upgrade head

# 5. Run the tests
pytest -v

# 6. Add a product to the dev database
docker exec cache-pg psql -U app -d cache_demo -c \
  "INSERT INTO product (name, price, description) VALUES ('Claude AI', 19.99, 'Best AI assistant');"

# 7. Start the API
uvicorn app.main:app --reload
```

Then try it:

```bash
# Caching
curl http://localhost:8000/products/1               # 1st call: miss, read from PostgreSQL
docker exec redis_cache redis-cli TTL product:1     # the key now exists, with its TTL in seconds
curl http://localhost:8000/products/1               # 2nd call: served from Redis

# Invalidation
curl -X PUT http://localhost:8000/products/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Claude AI", "price": "24.99", "description": "New price"}'
docker exec redis_cache redis-cli EXISTS product:1  # 0: the key was deleted
curl http://localhost:8000/products/1               # the new price, read from PostgreSQL

# Negative caching
curl http://localhost:8000/products/9999            # 404, read from PostgreSQL
docker exec redis_cache redis-cli GET product:9999  # "__not_found__"
docker exec redis_cache redis-cli TTL product:9999  # 60 seconds or less
```

## Design

- **Key:** `product:{id}`. **Value:** the product as JSON.
- **TTL:** 10 minutes, set in the same command as the value (`SET ... EX 600`). Redis deletes the key itself when the TTL runs out, so the app only checks whether the key exists.
- **Hit:** the key exists, so the product is returned from Redis and the database is not touched.
- **Miss:** the product is read from PostgreSQL, stored in Redis with the TTL, then returned.
- **Update (`PUT`):** the database is updated **first**, then the key is deleted. Deleting first would let a `GET` arriving in between read the old row and cache it again for 10 minutes. The key is deleted, not overwritten, so `GET` stays the only place that fills the cache.
- **Not found:** the app stores the marker `__not_found__` under the same key, with a TTL of 60 seconds, and returns 404. The next requests for that id get their 404 from Redis. The TTL is short so that a product created later isn't hidden for long, and so that requests for many random ids don't fill Redis.

Invalid ids (`0`, negative numbers, numbers above the PostgreSQL `integer` limit, non-integers) are rejected with 422 before any query runs. Invalid bodies on `PUT` (wrong types, missing fields, an empty name or one over 100 characters, a price of 0 or less, too many digits) are rejected with 422 the same way.

## Proof

There are 26 tests. They run against a separate test database (`cache_demo_test`) and Redis database 1, both emptied before each test, so they never touch dev data.

A counter, `db_reads`, goes up each time the app reads a product from PostgreSQL. The tests check it:

- **1st request:** `db_reads == 1`, and the product is now in Redis with a TTL.
- **2nd request for the same product:** `db_reads` is still `1`, so the database was not touched, and the response is identical.
- **After the key expires:** `db_reads == 2`, and the product is cached again.
- **After a `PUT`:** the key is gone, and the next `GET` returns the new data.
- **2nd request for an id that doesn't exist:** still a 404, and `db_reads` is still `1`.

## What's next

- **v3:** stampede protection, so many requests arriving right after a key expires cause only one database read.