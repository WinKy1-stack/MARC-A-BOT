# Contributing Guide

## 🔄 Development Workflow

```bash
# 1. Create branch
git checkout -b feature/your-feature

# 2. Code + Test
# ... write code ...
pytest tests/

# 3. Commit
git commit -m "feat(scope): description"

# 4. Push & PR
git push origin feature/your-feature
```

## 📝 Code Style

**Python**:
- Follow PEP 8
- Use type hints
- Add docstrings

**Naming**:
- Files: `lowercase_with_underscores.py`
- Classes: `PascalCase`
- Functions: `lowercase_with_underscores()`
- Constants: `UPPERCASE_WITH_UNDERSCORES`

## 🧪 Testing

```bash
# Write tests (80%+ coverage)
pytest tests/ --cov=services

# Run before commit
pytest tests/
```

## 💬 Commit Messages

Format: `<type>(<scope>): <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring

Examples:
```bash
feat(authority): add Dewey classification
fix(cache): resolve fuzzy matching bug
docs(api): update endpoint docs
```

## 🔀 Pull Request

**Checklist**:
- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No debug code

**Template**:
```markdown
## Changes
Brief description

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] Documentation

## Testing
- [ ] Tests pass
- [ ] Manual testing done
```

## 📁 Project Structure

**Adding new service**:
```
services/
└── your_service/
    ├── __init__.py
    ├── config.py
    ├── service.py
    └── clients/
```

**Adding API endpoint**:
```python
# api/your_routes.py
from flask import Blueprint

bp = Blueprint('name', __name__, url_prefix='/api/name')

@bp.route('/endpoint', methods=['POST'])
def endpoint():
    return jsonify({'status': 'ok'})
```

Register in `app.py`:
```python
from api.your_routes import bp
app.register_blueprint(bp)
```

## 📞 Support

Issues: https://github.com/LockMan04/MARC-A-BOT/issues
