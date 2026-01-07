# Contributing to Resume Ranking System

Thank you for your interest in contributing! This project focuses on evaluation and auditing of ML systems.

## How to Contribute

### 1. Improving Fairness Tests

**What to add:**
- New perturbation types
- Additional fairness metrics
- Better evaluation methodologies

**What NOT to add:**
- Sensitive attribute inference
- Prediction of protected characteristics
- Hiring decision logic

### 2. Enhancing Explainability

**Welcome contributions:**
- Better ablation methods
- Improved visualizations
- Novel explanation techniques

### 3. Documentation

**Always needed:**
- Usage examples
- Tutorial notebooks
- Improved documentation

## Code Guidelines

### Style
- Follow PEP 8
- Use type hints
- Add docstrings to all functions
- Run `black` for formatting

### Testing
- Add tests for new features
- Maintain >80% test coverage
- Run `pytest` before submitting

### Ethical Guidelines

**Must follow:**
1. **No Sensitive Attribute Inference**: Never add code that infers race, gender, age, etc.
2. **Clear Disclaimers**: All new features must include ethical disclaimers
3. **Evaluation Focus**: Contributions should focus on evaluation, not decision-making
4. **Transparency**: Document all assumptions and limitations

## Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature`
3. **Make your changes**
4. **Add tests**
5. **Update documentation**
6. **Run tests**: `pytest`
7. **Format code**: `black src/ tests/`
8. **Commit**: Use clear commit messages
9. **Push**: `git push origin feature/your-feature`
10. **Create PR**: Describe your changes clearly

## Review Criteria

Your PR will be evaluated on:
- **Ethical compliance**: Does it follow ethical guidelines?
- **Code quality**: Is it well-written and tested?
- **Documentation**: Is it properly documented?
- **Scope**: Does it fit the project's mission?

## Areas for Contribution

### High Priority
- [ ] More fairness tests (disability bias, age bias, etc.)
- [ ] Better visualizations
- [ ] Jupyter notebook tutorials
- [ ] Documentation improvements

### Medium Priority
- [ ] API enhancements
- [ ] Performance optimizations
- [ ] Additional baseline models
- [ ] More comprehensive tests

### Low Priority
- [ ] UI/dashboard (optional feature)
- [ ] Additional export formats
- [ ] Integration examples

## What We Won't Accept

❌ **Will be rejected:**
- Code that makes hiring decisions
- Sensitive attribute inference
- Overclaiming of capabilities
- Lack of ethical disclaimers
- Poor documentation

## Questions?

- Open an issue for discussion
- Tag it with `question` or `discussion`
- Be respectful and constructive

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Maintain ethical standards
- Prioritize fairness and transparency

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make this project better! 🎉
