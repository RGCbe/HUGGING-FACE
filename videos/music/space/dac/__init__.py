"""A stand-in for descript-audio-codec (dac), which Seed-VC imports only for its vector quantizer.

The singing model we use has vector_quantize: false and is_discrete: false, so the quantizer is never built.
This stub keeps the import working without installing dac and its many dependencies; using it is an error.
"""
