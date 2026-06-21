# Errors and Statuses

## Contents
- Status values
- Terminal statuses
- Error codes
- Pagination validation
- Response validation
- Logging rules

## Status values
- `QUEUED`
- `ACTIVE`
- `COMPLETED`
- `TIMED_OUT`
- `FAILED`

## Terminal statuses
- `COMPLETED`
- `TIMED_OUT`
- `FAILED`

## Error handling
Cover:
- 400 invalid request
- 401 missing/invalid API key
- 402 insufficient funds
- 403 unauthorized
- 404 not found
- 500 server error
- network timeout
- invalid response shape

## Logging
Never log:
- `LEMONSLICE_API_KEY`
- `X-API-Key`
- hosted Daily `token`
- LiveKit token
- Daily token
- raw Authorization headers
