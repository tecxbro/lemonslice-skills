# Hosted Daily state machine

`idle → creating_room → joining_daily → pipeline_ready → waiting_for_frame → active`

Terminal and retry transitions:

- backend/create failure → `retryable_failed`
- Daily join failure → `retryable_failed`
- startup timeout → leave/destroy → `retryable_failed`
- fatal `daily_error` → leave/destroy → `retryable_failed`
- agent participant leaves → `ended` or `retryable_failed` based on expected state
- user hangup → `ending` → `ended`
- retry → request fresh backend credentials, never reuse token
