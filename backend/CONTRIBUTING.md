# Contributing to DeepCheck AI 🤝

Thank you for your interest in contributing to DeepCheck AI! We welcome contributions from developers of all backgrounds and skill levels. This guide will help you get started with contributing to our deepfake detection service.

---

## 🌟 Ways to Contribute

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new features or improvements
- 📝 **Documentation**: Improve our docs, examples, and tutorials
- 🔧 **Code Contributions**: Submit bug fixes, new features, or optimizations
- 🧪 **Testing**: Add test cases or improve test coverage
- 🎨 **UI/UX**: Enhance the user experience
- 📊 **Performance**: Optimize models and processing pipelines

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.8+** installed
- **Git** configured with your GitHub account
- Basic knowledge of **Python**, **Flask/FastAPI**, and **AI/ML concepts**
- Familiarity with **deepfake detection** (helpful but not required)

### Development Environment Setup

1. **Fork the repository**

   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/deepcheck-ai.git
   cd deepcheck-ai
   ```

2. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/deepcheck-ai.git
   ```

3. **Create virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   # Install main dependencies
   pip install -r requirements.txt

   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

5. **Set up pre-commit hooks** (optional but recommended)

   ```bash
   pre-commit install
   ```

6. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your development settings
   ```

7. **Verify installation**
   ```bash
   python run.py
   # Should start the development server without errors
   ```

---

## 🔄 Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your work:

```bash
# Sync with upstream
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description

# Or for documentation
git checkout -b docs/improvement-description
```

### Branch Naming Convention

- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `docs/` - Documentation improvements
- `test/` - Adding or improving tests
- `refactor/` - Code refactoring
- `perf/` - Performance improvements

### 2. Make Your Changes

#### Code Style Guidelines

We follow **PEP 8** standards with some specific conventions:

```python
# Use descriptive variable names
confidence_score = model.predict(image)  # ✅ Good
cs = model.pred(img)  # ❌ Avoid

# Add type hints
def analyze_image(image_path: str, threshold: float = 0.5) -> dict:
    """Analyze image for deepfake detection."""
    pass

# Include comprehensive docstrings
def preprocess_video(video_path: str) -> np.ndarray:
    """
    Preprocess video file for deepfake analysis.

    Args:
        video_path (str): Path to the video file

    Returns:
        np.ndarray: Preprocessed video frames

    Raises:
        ValueError: If video file is invalid or corrupted
    """
    pass
```

#### Code Formatting

We use **Black** for code formatting:

```bash
# Format your code
black app/ tests/

# Check formatting (CI will run this)
black --check app/ tests/
```

#### Import Organization

Use **isort** for import sorting:

```bash
# Sort imports
isort app/ tests/

# Check import sorting
isort --check-only app/ tests/
```

### 3. Testing Your Changes

#### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

#### Writing New Tests

Add tests for new functionality:

```python
# tests/test_new_feature.py
import pytest
from app.models.image_detector import ImageDetector

class TestImageDetector:
    def test_valid_image_analysis(self):
        """Test image analysis with valid input."""
        detector = ImageDetector()
        result = detector.analyze("tests/fixtures/real_image.jpg")

        assert result['is_deepfake'] is False
        assert 0 <= result['confidence'] <= 1
        assert result['processing_time'] > 0

    def test_invalid_image_path(self):
        """Test handling of invalid image path."""
        detector = ImageDetector()

        with pytest.raises(FileNotFoundError):
            detector.analyze("nonexistent_file.jpg")
```

### 4. Documentation

#### Code Documentation

- Add docstrings to all public functions and classes
- Include type hints for parameters and return values
- Document any complex algorithms or business logic
- Add inline comments for non-obvious code sections

#### API Documentation

Update API documentation when adding new endpoints:

```python
@app.route('/api/analyze', methods=['POST'])
def analyze_media():
    """
    Analyze uploaded media for deepfake detection.

    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Media file to analyze
      - name: threshold
        in: formData
        type: number
        required: false
        description: Confidence threshold (0.0-1.0)
    responses:
      200:
        description: Analysis complete
        schema:
          type: object
          properties:
            is_deepfake:
              type: boolean
            confidence:
              type: number
    """
    pass
```

### 5. Commit Your Changes

#### Commit Message Convention

We follow the **Conventional Commits** standard:

```bash
# Format: <type>[optional scope]: <description>

git commit -m "feat: add audio deepfake detection support"
git commit -m "fix: resolve memory leak in video processing"
git commit -m "docs: update API documentation with new endpoints"
git commit -m "test: add unit tests for image preprocessing"
git commit -m "refactor: optimize model loading performance"
```

#### Commit Types

- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or modifying tests
- `chore` - Maintenance tasks, dependency updates

### 6. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
# Fill out the PR template with detailed information
```

---

## 📝 Pull Request Guidelines

### PR Checklist

Before submitting your PR, ensure:

- [ ] Code follows our style guidelines (PEP 8)
- [ ] All tests pass locally
- [ ] New functionality includes appropriate tests
- [ ] Documentation has been updated
- [ ] Commit messages follow our convention
- [ ] PR description clearly explains the changes
- [ ] No merge conflicts with main branch

### PR Template

When creating a PR, use this template:

```markdown
## Description

Brief description of the changes and the problem they solve.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?

Describe the tests you ran and provide instructions to reproduce.

## Screenshots (if applicable)

Add screenshots to help explain your changes.

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

---

## 🎯 Contribution Areas

### High Priority Areas

1. **Model Performance** 🚀

   - Optimize inference speed
   - Reduce memory usage
   - Improve accuracy metrics
   - Add new detection algorithms

2. **API Improvements** 🌐

   - Add batch processing endpoints
   - Implement async processing
   - Enhance error handling
   - Add rate limiting

3. **Documentation** 📚

   - API examples and tutorials
   - Model architecture explanations
   - Deployment guides
   - Contributing guides

4. **Testing & Quality** 🧪
   - Increase test coverage
   - Add integration tests
   - Performance benchmarks
   - Security testing

### Good First Issues

New contributors can start with these areas:

- 📖 **Documentation improvements**
- 🐛 **Bug fixes** (labeled as "good first issue")
- 🧪 **Writing unit tests**
- 🔧 **Configuration enhancements**
- 📊 **Adding logging and monitoring**

---

## 🔍 Code Review Process

### What We Look For

1. **Code Quality**

   - Clean, readable code
   - Proper error handling
   - Efficient algorithms
   - Security best practices

2. **Testing**

   - Adequate test coverage
   - Edge case handling
   - Integration test compatibility

3. **Documentation**
   - Clear docstrings
   - Updated README if needed
   - API documentation updates

### Review Timeline

- Initial review: Within 2-3 business days
- Follow-up reviews: Within 1-2 business days
- Merge after approval: Within 1 business day

---

## 🏷️ Issue Labels

Understanding our label system:

| Label              | Description                                |
| ------------------ | ------------------------------------------ |
| `bug`              | Something isn't working                    |
| `enhancement`      | New feature or request                     |
| `good first issue` | Good for newcomers                         |
| `help wanted`      | Extra attention is needed                  |
| `documentation`    | Improvements or additions to documentation |
| `priority: high`   | High priority issues                       |
| `priority: low`    | Low priority issues                        |
| `wontfix`          | This will not be worked on                 |

---

## 🛠️ Development Tips

### Performance Optimization

```python
# Use appropriate data types
import numpy as np

# Efficient image processing
def preprocess_image_batch(images: List[np.ndarray]) -> np.ndarray:
    """Process multiple images efficiently."""
    # Vectorized operations are faster
    batch = np.stack(images)
    return (batch / 255.0).astype(np.float32)

# Memory management
def analyze_large_video(video_path: str) -> dict:
    """Analyze video with memory efficiency."""
    # Process in chunks to avoid memory issues
    chunk_size = 32
    # Implementation details...
```

### Error Handling Best Practices

```python
import logging
from typing import Optional

def safe_model_inference(image_data: np.ndarray) -> Optional[dict]:
    """Perform model inference with proper error handling."""
    try:
        result = model.predict(image_data)
        return {
            'success': True,
            'confidence': float(result.confidence),
            'is_deepfake': bool(result.prediction)
        }
    except Exception as e:
        logging.error(f"Model inference failed: {str(e)}")
        return None
```

### Configuration Management

```python
# config/settings.py
from typing import List, Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings with validation."""

    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=5000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")

    # Model settings
    model_path: str = Field(..., env="MODEL_PATH")  # Required
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)

    # File processing
    max_file_size: int = Field(default=100 * 1024 * 1024)  # 100MB
    supported_formats: List[str] = ["jpg", "jpeg", "png", "mp4", "wav"]

    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

## ❓ Getting Help

### Communication Channels

- 💬 **GitHub Discussions**: For general questions and feature discussions
- 🐛 **GitHub Issues**: For bug reports and specific problems
- 📧 **Email**: technical-support@deepcheck-ai.com
- 🗨️ **Discord**: [Join our developer community](https://discord.gg/deepcheck-ai)

### Common Issues

**Q: My tests are failing locally but pass on CI**
A: Ensure you're using the same Python version and dependencies as CI. Check the GitHub Actions configuration.

**Q: How do I add a new detection model?**
A: Create a new model class inheriting from `BaseDetector`, implement required methods, and add tests. See existing models for examples.

**Q: The development server won't start**
A: Check your `.env` configuration and ensure all dependencies are installed. Run `pip install -r requirements-dev.txt`.

---

## 🎉 Recognition

We believe in recognizing our contributors! Here's how we show appreciation:

### Contributor Recognition

- 🏆 **Contributors.md**: Your name will be added to our contributors list
- 🎖️ **GitHub Badges**: Earn contributor badges for different types of contributions
- 📢 **Social Media**: We highlight significant contributions on our social channels
- 🎁 **Swag**: Active contributors receive DeepCheck AI merchandise

### Contribution Levels

- **First-time Contributor**: First merged PR
- **Regular Contributor**: 5+ merged PRs
- **Core Contributor**: 20+ merged PRs or significant feature contributions
- **Maintainer**: Ongoing project maintenance and code reviews

---

## 📚 Additional Resources

### Learning Resources

- **[Deepfake Detection Papers](https://github.com/papers/deepfake-detection)** - Academic research
- **[Computer Vision Fundamentals](https://docs.opencv.org/4.x/d9/df8/tutorial_root.html)** - OpenCV tutorials
- **[PyTorch Deep Learning](https://pytorch.org/tutorials/)** - PyTorch tutorials
- **[API Design Best Practices](https://restfulapi.net/)** - REST API guidelines

### Development Tools

- **[VS Code Extensions](https://marketplace.visualstudio.com/items?itemName=ms-python.python)** - Python development
- **[PyCharm](https://www.jetbrains.com/pycharm/)** - Professional IDE
- **[Git Hooks](https://pre-commit.com/)** - Code quality automation
- **[Docker Desktop](https://www.docker.com/products/docker-desktop)** - Containerization

---

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). We are committed to providing a welcoming and inspiring community for all.

### Our Pledge

We pledge to make participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

---

## 📄 License

By contributing to DeepCheck AI, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

<p align="center">
  <strong>Thank you for contributing to DeepCheck AI! 🙏</strong><br>
  <em>Together, we're building a safer digital world.</em>
</p>
