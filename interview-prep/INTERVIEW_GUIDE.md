# Interview Preparation Guide

## Technical Interview Questions

### Q: Why build this instead of just using SBERT?

> "Production hiring systems combine semantic understanding with structured signals like education and employment history. I wanted to measure fairness **at the architecture level** — can we audit a system where prestige effects are explicit vs accidental? The hybrid design makes counterfactual testing meaningful: swapping MIT↔Unknown actually changes rankings (Δ=1.76), whereas pure embeddings can't measure this (Δ=0.00)."

### Q: What's the hardest part of fairness auditing?

> "**Defining the counterfactual**. For university swap, I had to choose: do we replace text mentions only, or simulate candidate pool shifts? I chose text replacement to isolate the scoring mechanism. For gender, pronoun swap is imperfect (misses implicit signals in writing style), but it's transparent and reproducible. The key is documenting limitations upfront."

### Q: How would you productionize this?

> "Three changes:
> 1. **Configurable weights**: Move 70/15/10/5 to YAML so stakeholders can run sensitivity analysis
> 2. **Audit logs**: Track every ranking with component scores (semantic vs education vs continuity)
> 3. **Threshold alerts**: Flag candidates where education/continuity signals dominate semantic fit (e.g., education > 40% of total score)
>
> The goal isn't to eliminate structured signals — it's to make them **visible, tunable, and accountable**."

---

## Key Technical Insights

### Why Hybrid Architecture?

Production hiring systems combine semantic understanding with explicit structured signals. Pure embeddings under-represent education and continuity biases that real stakeholders care about measuring.

**Evidence**:
- University swap: Hybrid Δ=1.76 vs Semantic Δ=0.00
- Gap insertion: Hybrid Δ=2.14 vs Semantic Δ=0.00

### Design Decisions

1. **No fine-tuning**: Pretrained SBERT maintains reproducibility and avoids overfitting to synthetic data
2. **Explicit weights**: 70/15/10/5 split makes signals auditable and tunable
3. **Tier-based education**: Simple, transparent mapping vs complex ML model
4. **Pattern-based gaps**: Regex detection is interpretable and debuggable

### Architecture Tradeoffs

| Choice | Pros | Cons |
|--------|------|------|
| **Hybrid scoring** | Auditable, measurable bias | More complex than pure embeddings |
| **Fixed weights** | Reproducible, transparent | No adaptive learning |
| **4-tier education** | Simple, interpretable | Subjective tier assignment |
| **Pattern gap detection** | Fast, explainable | Misses nuanced narratives |

---

## Demo Walkthrough (2-3 minutes)

### Opening (30 seconds)
"This is a fairness auditing framework for resume ranking systems. The key insight: production systems combine semantic embeddings with structured signals like education prestige. I built a hybrid architecture to make those signals explicit and measurable."

### Core Feature (60 seconds)
"The system runs counterfactual tests — swapping universities, redacting names, inserting employment gaps. For example, when I swap a tier-3 university with MIT, the hybrid ranker shows a rank change of 1.76 positions. Pure SBERT shows zero change, because the effect is hidden in embeddings."

### Technical Depth (45 seconds)
"The architecture weights semantic similarity at 70%, education at 15%, employment continuity at 10%. This mirrors production systems at companies like Lever or Greenhouse, where structured signals matter but need to be auditable."

### Impact (15 seconds)
"The result: ML engineers can measure fairness at the architecture level, not just model level. It's an evaluation tool, not a hiring product."

---

## Handling Tough Questions

### "Why not fine-tune SBERT?"
> "Fine-tuning risks overfitting to my specific dataset. Pretrained models maintain generalizability. In production, you'd fine-tune on company-specific data with proper validation — but for an audit framework, reproducibility matters more than marginal accuracy gains."

### "Why only 400 resumes?"
> "This is an evaluation and audit framework, not a production ranker. 400 resumes is sufficient to demonstrate counterfactual testing methodology. Production systems would use millions, but the architectural insights transfer."

### "Isn't this biased by design?"
> "Yes — intentionally. The hybrid architecture makes bias **explicit** so it can be measured, tuned, and audited. That's the point. Pure embeddings hide bias in latent space where stakeholders can't control it."

### "What about other fairness metrics?"
> "I focused on rank-based metrics (Δ position, affected %) because they're interpretable to non-technical stakeholders. Demographic parity or equalized odds would require protected attribute labels, which raises privacy concerns. My approach uses behavioral perturbations instead."

---

## Project Positioning

### What This Project Shows

✅ **Systems thinking**: Hybrid architecture reflects production realism  
✅ **Evaluation discipline**: 3-way ablation study (Hybrid, Semantic, TF-IDF)  
✅ **Restraint**: No fine-tuning, no overclaiming  
✅ **Responsibility**: Limitations documented, ethical framing

### What This Project Is NOT

❌ A hiring automation tool  
❌ A classification model  
❌ A claim about "solving bias"  
❌ A production-ready system

### Differentiation

**vs RAG chatbot projects**: Shows ranking + fairness, not just retrieval  
**vs Fine-tuning demos**: Shows architectural judgment, not just GPU access  
**vs Kaggle notebooks**: Shows system design, not just model accuracy

---

## Technical Deep Dives (If Asked)

### Counterfactual Design Choices

**University Swap**:
- Replaces tier-3 → tier-1 mentions in resume text
- Isolates scoring mechanism, not recruitment pipeline
- Limitation: Doesn't capture prestige effects in recommendations

**Pronoun Swap**:
- Replaces he/she/him/her across all resumes
- Tests semantic co-occurrence patterns, not explicit gender modeling
- Limitation: Misses implicit bias in writing style

**Gap Insertion**:
- Adds "Career break (18 months)" to employment section
- Tests continuity penalty in scoring logic
- Limitation: Pattern-based, doesn't model all career narratives

### Why These Metrics?

**ΔRank (mean absolute change)**:
- Interpretable: "On average, candidates move X positions"
- Sensitive to both upward and downward shifts

**Affected %**:
- Scope indicator: "Y% of candidates see rank changes"
- Complements ΔRank (small changes affecting many vs large changes affecting few)

**Distribution plots (boxplots)**:
- Shows risk profiles, not just means
- Reveals outliers and variance

---

## Code Walkthrough (If Asked)

### Hybrid Ranker Core Logic

```python
def rank(self, resumes, job_description, return_components=False):
    # Semantic component (70%)
    semantic_scores = self.semantic_ranker.rank(resumes, job_description)
    
    # Education component (15%)
    education_scores = [self._calculate_education_score(r) for r in resumes]
    
    # Continuity component (10%)
    continuity_scores = [self._calculate_continuity_score(r) for r in resumes]
    
    # Weighted combination
    final_scores = (
        0.70 * semantic_scores +
        0.15 * education_scores +
        0.10 * continuity_scores +
        0.05 * np.ones(len(resumes))  # Reserved
    )
    
    return final_scores
```

**Key insight**: Each component is independently calculated and transparently weighted.

### Fairness Test Structure

```python
def test_university_swap(self, ranker, resumes, job_description):
    # Baseline ranking
    baseline_ranks = ranker.rank(resumes, job_description)
    
    # Perturbed data
    perturbed_resumes = [swap_university(r) for r in resumes]
    
    # Perturbed ranking
    perturbed_ranks = ranker.rank(perturbed_resumes, job_description)
    
    # Metrics
    rank_changes = np.abs(baseline_ranks - perturbed_ranks)
    return {
        'mean_rank_change': np.mean(rank_changes),
        'affected_pct': (rank_changes > 0.5).mean() * 100
    }
```

**Key insight**: Controlled comparison with single-variable perturbation.

---

## Closing Statement

"This project demonstrates that fairness auditing requires architectural thinking, not just better embeddings. By making structured signals explicit, we enable stakeholders to measure, tune, and debate what matters — rather than trusting a black box."
