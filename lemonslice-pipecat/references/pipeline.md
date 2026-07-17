# Pipecat pipeline reference

```python
pipeline = Pipeline([
    transport.input(),
    stt,
    user_aggregator,
    llm,
    tts,
    transport.output(),
    assistant_aggregator,
])
```

LemonSlice uses Daily under the hood. The avatar is not a human participant, its microphone is muted to avoid feedback, and the transport manages `interrupt`, `response_started`, and `response_finished`.
