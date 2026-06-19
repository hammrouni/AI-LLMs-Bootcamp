"""
04 - Measuring Latency & Throughput Demo
========================================
Measures TTFT and tokens-per-second on a local Ollama model. Reports median
of several runs after a warmup.

WHY MEASURE LATENCY?
    "It feels slow" is not a metric. Without numbers, you can't diagnose:
      - Is the FIRST token slow? (model loading / prefill issue)
      - Is EVERY token slow? (CPU bottleneck / no GPU offload)
      - Is the retriever the bottleneck, not the LLM?
      - Is it slow only for LONG prompts? (context scaling issue)

    You need numbers, not feelings.

KEY CONCEPTS:
    TTFT (Time-To-First-Token):
        How long until the first character appears on screen.
        This is what users perceive as "responsiveness".
        A streaming UI with low TTFT feels fast even if total time is high.

    TPOT (Time-Per-Output-Token):
        Average time to generate each subsequent token after the first.
        Determines how fast text "flows" during streaming.

    Tokens/sec (tok/s):
        = 1 / TPOT. The standard throughput metric.
        Higher = faster sustained generation.

    Prefill:
        The cost of processing the input prompt BEFORE generating.
        Longer prompts → longer prefill → higher TTFT.

    Decode:
        The cost of generating each output token one by one.
        This is where GPU parallelism helps the most.

    KV Cache:
        Ollama reuses computation from the input across turns,
        so follow-up messages in a conversation have lower TTFT.

    Analogy — Tunisian café:
        TTFT   = time until your espresso arrives at the table
        TPOT   = how fast each next sip is poured
        tok/s  = how many espressos the café serves per hour

REASONABLE TARGETS:
    | Metric                      | Good     | Acceptable | Bad    |
    |-----------------------------|----------|------------|--------|
    | TTFT                        | < 500 ms | < 1.5 s    | > 3 s  |
    | tok/s (7B Q4)               | 30+ GPU  | 8-15 CPU   | < 5    |
    | Total for 100-token answer  | < 2 s    | < 8 s      | > 15 s |

HOW TO RUN THIS FILE:
1. ollama serve
2. ollama pull mistral
3. pip install ollama
4. python demo.py
"""

import time
import statistics


def pick_model():
    """
    Auto-detect which model is already pulled in Ollama.
    Checks common small models in order of preference: mistral > phi3 > llama3.
    Returns the model name string, or None if nothing is available.
    """
    try:
        import ollama
    except ImportError:
        return None
    try:
        info = ollama.list()
    except Exception:
        return None
    names = [m.get("name") or m.get("model") for m in info.get("models", [])]
    for cand in ["mistral", "mistral:latest", "phi3", "llama3"]:
        for n in names:
            if cand in n:
                return n
    return None


def benchmark(model, prompt, runs=3, num_predict=120):
    """
    Measure TTFT, tokens/sec, and total time for a given model and prompt.

    Why this function exists:
        A single timed run is noisy — OS scheduling, garbage collection, and
        Ollama's internal caching all add variance. Running multiple times and
        taking the median gives a stable, reproducible number.

    How it works step by step:
        1. WARMUP: A tiny generate() call loads the model into memory.
           Without this, the first real run includes model loading time,
           which inflates TTFT and makes the measurement useless.
        2. STREAMING: We use stream=True so we can capture the exact moment
           the first token arrives (TTFT), not just total completion time.
        3. MULTIPLE RUNS: We repeat `runs` times and collect all metrics.
        4. MEDIAN: statistics.median() is more robust than mean — a single
           outlier (e.g., GC pause) doesn't skew the result.

    Parameters:
        model       — Ollama model name (e.g., "mistral:latest")
        prompt      — The user prompt to benchmark
        runs        — Number of repetitions (default 3; more = more stable)
        num_predict — Max tokens to generate per run (caps output length)

    Returns dict with:
        ttft_ms_median  — Median time-to-first-token in milliseconds
        tps_median      — Median tokens per second (sustained generation speed)
        total_s_median  — Median total wall-clock time in seconds
        tokens_approx   — Approximate token count from the last run
        runs            — Number of runs performed
    """
    import ollama

    # STEP 1: Warmup — force model loading so it doesn't count in measurements.
    # Ollama loads models lazily; the first request pays the loading cost.
    # A 5-token generation is enough to load the model without wasting time.
    ollama.generate(model=model, prompt="warmup", options={"num_predict": 5})

    ttfts, tpss, totals = [], [], []

    for _ in range(runs):
        # STEP 2: Start the high-resolution timer.
        # perf_counter() gives sub-millisecond precision — essential for TTFT.
        start = time.perf_counter()
        first_token_time = None
        tokens = 0

        # STEP 3: Stream the response token by token.
        # stream=True makes Ollama send each chunk as it's generated,
        # rather than waiting for the full response. This lets us measure
        # TTFT — the time between sending the request and receiving the
        # first non-empty chunk.
        for chunk in ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            options={
                "num_predict": num_predict,  # cap output length for consistent benchmarks
                "temperature": 0.2,          # low temp = more deterministic = less variance between runs
            },
        ):
            txt = chunk["message"]["content"]
            # Record the timestamp of the FIRST non-empty token
            if first_token_time is None and txt:
                first_token_time = time.perf_counter()
            # Count tokens (approximated by word count)
            if txt:
                tokens += max(1, len(txt.split()))

        # STEP 4: Calculate metrics for this run
        end = time.perf_counter()
        total = end - start                                     # total wall-clock time
        ttft = (first_token_time - start) if first_token_time else total  # time to first token
        tps = tokens / max(total, 1e-6)                         # tokens per second (avoid division by zero)

        ttfts.append(ttft)
        tpss.append(tps)
        totals.append(total)

    # STEP 5: Return medians, not means.
    # Median of [0.02, 0.02, 0.5] = 0.02 (ignores the outlier)
    # Mean of  [0.02, 0.02, 0.5] = 0.18 (skewed by the outlier)
    return {
        "ttft_ms_median": statistics.median(ttfts) * 1000,  # convert seconds → milliseconds
        "tps_median":     statistics.median(tpss),
        "total_s_median": statistics.median(totals),
        "tokens_approx":  tokens,
        "runs":           runs,
    }


# ============================================================
# PART 1: Problem — "It feels slow"
# ============================================================
# Scenario: You ship a local chatbot for a Tunisian e-commerce site.
# Users complain it's slow. But WHERE is the slowness?
#
#   Possible causes:
#   1. Prefill is slow  → long input prompt takes ages to process
#   2. Decode is slow   → each output token takes too long (CPU-bound)
#   3. Retriever is slow → the RAG retrieval step is the bottleneck
#   4. Only long prompts → short prompts are fine, long ones are not
#
# Without measuring TTFT and tok/s separately, you're guessing.
# You might optimize the wrong thing entirely.
# ============================================================

def show_the_problem():
    """
    Explains why subjective impressions ("it feels slow") are useless
    for diagnosing performance issues. You need two numbers:
      - TTFT (time-to-first-token): is the START slow?
      - tok/s (tokens per second):  is the GENERATION slow?

    These point to completely different fixes:
      - High TTFT → reduce prompt length, use KV cache, check model loading
      - Low tok/s → enable GPU, use smaller quantization, reduce num_predict
    """
    print("=== PART 1: 'It Feels Slow' Is Not Enough ===\n")
    print("Without numbers you cannot diagnose:")
    print("  - Is the prefill (input) slow?")
    print("  - Is decode (output) slow?")
    print("  - Is the retriever the bottleneck?")
    print("  - Is it slow only for long prompts?")
    print("Measurement is step one.\n")


# ============================================================
# PART 2: Solution — A Simple Benchmark Function
# ============================================================
# The solution is a reusable benchmark() function that:
#
# 1. WARMS UP the model (eliminates cold-start noise)
# 2. STREAMS the response (captures TTFT precisely)
# 3. REPEATS N times (reduces run-to-run variance)
# 4. Returns MEDIANS (robust to outliers like GC pauses)
#
# BAD approach (what most people do):
#   start = time.time()
#   ollama.generate(model="mistral", prompt="...")
#   print(time.time() - start)
#   # → Noisy, includes cold-start, no TTFT, single run
#
# GOOD approach (what benchmark() does):
#   ttft, tps = benchmark("mistral", "Tell me about Sfax.", runs=5)
#   # → Stable median, warm model, TTFT separated from total
# ============================================================

def show_the_solution():
    """
    Describes the benchmark function's design — printed as a quick summary
    so the user knows what Part 3 will actually run.
    """
    print("=== PART 2: Benchmark Function ===\n")
    print("benchmark(model, prompt, runs=3, num_predict=120):")
    print("  1. Warm up the model with a tiny call")
    print("  2. Stream the real prompt N times")
    print("  3. Capture TTFT, total time, and tokens/sec")
    print("  4. Return medians (robust to outliers)\n")


# ============================================================
# PART 3: Real Benchmark
# ============================================================
# We test THREE different prompt lengths to see how latency scales:
#
#   - "short"  → simple factual question (few input tokens)
#   - "medium" → requires a short explanation (moderate input)
#   - "long"   → asks for a detailed story (many input tokens)
#
# Why test different lengths?
#   Prefill time scales with input length. A model that feels fast on
#   "Name three cities" might feel slow on a 500-word RAG context.
#   Testing multiple lengths reveals whether TTFT increases with
#   prompt size (prefill bottleneck) or stays flat (good sign).
#
# What to look for in the results table:
#   - TTFT (ms): Should be < 500ms for a good user experience.
#                If it jumps significantly for "long", prefill is the bottleneck.
#   - tok/s:     Should be consistent across all prompt lengths.
#                If it drops for "long", the model may be swapping to CPU.
#   - total (s): Total wall-clock time. Useful for SLA planning
#                ("can we guarantee < 3s answers?").
# ============================================================

def real_world_example():
    """
    Runs the benchmark on short, medium, and long prompts and prints
    a comparison table. This is the practical payoff of the demo —
    real numbers you can use to decide if your setup is production-ready.
    """
    print("=== PART 3: Real Benchmark ===\n")

    try:
        import ollama  # noqa
    except ImportError:
        print("Run: pip install ollama")
        return

    model = pick_model()
    if not model:
        print("Pull a model first: ollama pull mistral")
        return

    # Three prompts of increasing complexity.
    # Short prompts test raw TTFT; long prompts stress the prefill stage.
    prompts = [
        ("short",  "Name three Tunisian cities."),
        ("medium", "Explain in 3 sentences why Sfax is famous for olives."),
        ("long",   "Write a 6-sentence story about Bilel discovering a hidden olive press in the Sfax countryside, with vivid sensory details."),
    ]

    print(f"Model: {model}\n")
    print(f"{'label':<8} {'TTFT (ms)':>10} {'tok/s':>8} {'total (s)':>10}")
    print("-" * 42)

    for label, prompt in prompts:
        # 3 runs per prompt, median reported — stable enough for a quick check.
        # For production benchmarking, increase to runs=10.
        m = benchmark(model, prompt, runs=3, num_predict=200)
        print(f"{label:<8} {m['ttft_ms_median']:>10.0f} {m['tps_median']:>8.1f} {m['total_s_median']:>10.2f}")
    print()


# ============================================================
# MAIN
# ============================================================
# The demo follows the optimization cycle:
#
#   Part 1: UNDERSTAND what to measure (TTFT vs tok/s)
#   Part 2: BUILD a repeatable benchmark function
#   Part 3: RUN it on real prompts and read the results
#
# After running, you have ship-worthy proof:
#   "TTFT median 22ms, 129 tok/s on mistral 7B Q4"
# instead of:
#   "The bot feels fast" (useless, can't repeat)
#
# Next steps after measuring:
#   - TTFT too high?  → Reduce prompt length, use KV cache, check GPU
#   - tok/s too low?  → Enable GPU (Day 03), use smaller quantization (Day 02)
#   - Both fine?      → Ship it, measure again in production under load
# ============================================================

if __name__ == "__main__":
    show_the_problem()       # Step 1: Why subjective "feels slow" fails
    show_the_solution()      # Step 2: How the benchmark function works
    real_world_example()     # Step 3: Run it, read the numbers

    print("--- Key Takeaways ---")
    print("1. TTFT is what users feel as 'responsiveness'.")
    print("2. Tokens/sec is the sustained generation speed.")
    print("3. Always warm up before measuring.")
    print("4. Take the median of several runs, not a single value.")
    print("5. Measure with prompts of different lengths — they behave differently.")
