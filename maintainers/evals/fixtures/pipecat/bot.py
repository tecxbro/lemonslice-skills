from pipecat.pipeline.pipeline import Pipeline

def build(transport, stt, llm, tts):
    return Pipeline([transport.input(), stt, llm, tts, transport.output()])
