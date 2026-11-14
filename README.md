# ODRA Payment Adapter

ODRA Payment Adapter is a Python-based payment integration project built with **FastAPI**. It demonstrates how an application can communicate with the Chapa payment gateway through a provider-based architecture.

The project supports payment initialization, payment verification, and callback handling. It is designed as a learning project using Chapa's test environment.

## Features

- Initialize payments through the Chapa API.
- Generate unique transaction references (`tx_ref`).
- Redirect customers using the Chapa checkout URL.
- Verify payment transactions with Chapa.
- Handle payment callbacks and independently verify transactions.
- Validate payment amounts and currencies.
- Handle common payment gateway errors and request timeouts.
- Validate incoming order data using Pydantic.
- Automated endpoint tests using Pytest.

## Technologies Used

- **Python 3.12**
- **FastAPI** - REST API framework.
- **Pydantic** - Request data validation.
- **HTTPX** - HTTP communication with Chapa.
- **Uvicorn** - ASGI server.
- **Python-dotenv** - Environment variable management.
- **Pytest** - Automated testing.

## Project Structure

```text
pay-adapter/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── order.py
│   │
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       └── chapa.py
│
├── tests/
│   └── test_main.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

### Architecture

The project uses a provider-based architecture to separate payment gateway operations from the API endpoints.

- `main.py`: Defines the API endpoints and handles payment-related requests.
- `config.py`: Loads application configuration and environment variables.
- `models/order.py`: Defines and validates incoming order data.
- `providers/base.py`: Defines the abstract payment provider interface.
- `providers/chapa.py`: Implements Chapa-specific payment operations.
- `tests/test_main.py`: Contains automated tests for the API.

The abstract provider interface makes it easier to introduce another payment provider in the future without redesigning the entire API.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/abiy-71/odra-payment-adapter.git
cd odra-payment-adapter
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root directory:

```env
APP_NAME=ODRA Payment Adapter
CHAPA_SECRET_KEY=your_chapa_secret_key
CHAPA_BASE_URL=https://api.chapa.co/v1
CALLBACK_URL=http://localhost:8000/payments/callback
```

Replace `your_chapa_secret_key` with your Chapa test secret key.

**Important:** Never commit your `.env` file or expose your secret API key publicly.

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks API health |
| POST | `/payments` | Initializes a payment |
| POST | `/payments/callback` | Handles payment callbacks |
| GET | `/payments/{tx_ref}` | Verifies a payment transaction |

### 1. Health Check

**GET** `/health`

Checks whether the application is running.

Example response:

```json
{
  "status": "ok"
}
```

### 2. Initialize Payment

**POST** `/payments`

Accepts an order and sends a payment initialization request to Chapa.

Example request:

```json
{
  "order_id": 10,
  "amount": "25.00",
  "email": "customer@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

Example response:

```json
{
  "tx_ref": "generated_transaction_reference",
  "checkout_url": "https://checkout.chapa.co/..."
}
```

The customer can use the returned checkout URL to proceed with payment.

### 3. Payment Callback

**POST** `/payments/callback`

Receives a callback containing the Chapa transaction reference.

Example request:

```json
{
  "trx_ref": "generated_transaction_reference"
}
```

The application uses the transaction reference to independently verify the payment with Chapa instead of trusting the callback data alone.

It also checks whether the verified transaction amount and currency match the original order.

### 4. Verify Payment

**GET** `/payments/{tx_ref}`

Verifies an existing payment using its transaction reference.

The application requests transaction details from Chapa and checks the transaction reference, amount, and currency against the original order.

## Running Tests

The project uses Pytest for automated testing.

Run the test suite with:

```bash
python -m pytest -v
```

The tests cover:

- Health check.
- Payment initialization.
- Invalid order amounts.
- Payment verification.
- Callback handling.
- Missing payment records and transaction references.
- Gateway timeouts.
- HTTP errors and connection failures.
- Payment amount and currency mismatches.

## Current Limitations

This project is built for learning and demonstration purposes. It currently uses Chapa's test environment and in-memory storage, with a single payment provider. Additional security and persistent database storage would be required for production use.

---

**Author:** Abiy Shita

**Project:** ODRA Payment Adapter